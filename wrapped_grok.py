import time
import threading
import logging
import re
import subprocess
from typing import Optional, Callable, List, Dict
from queue import Queue
import requests

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('violations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WrappedGrok')

try:
    from serpapi import GoogleSearch
except ImportError:
    # Fallback for different package structures
    try:
        from serpapi.google_search import GoogleSearch
    except ImportError:
        logger.warning("SerpAPI not installed. Web search features disabled.")
        GoogleSearch = None

# Audio support - required for voice chat
try:
    import speech_recognition as sr
    try:
        import pyaudio
        AUDIO_AVAILABLE = True
        logger.info("Audio support initialized successfully")
    except ImportError:
        logger.warning("PyAudio not installed. Voice chat requires PyAudio.")
        logger.warning("Install with: brew install portaudio && pip install pyaudio")
        AUDIO_AVAILABLE = False
        sr = None
except ImportError:
    AUDIO_AVAILABLE = False
    sr = None
    logger.warning("SpeechRecognition not installed. Voice chat disabled.")


class WrappedGrok:
    """
    WrappedGrok enforces:
    - Respond only after silence detection via timeout
    - Output max ten words unless 'explain' keyword detected
    - Always search web for factual claims using requests and SerpAPI
    - Listen live, cut own speech if English input starts
    - Log violations
    """
    
    def __init__(
        self,
        grok_api_key: str,
        serpapi_key: str,
        silence_timeout: float = 2.0,
        max_response_words: int = 10,
        explain_keyword: str = 'explain',
        elevenlabs_api_key: Optional[str] = None,
        elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel - clear female voice
        use_elevenlabs: bool = True
    ):
        """
        Initialize WrappedGrok.
        
        Args:
            grok_api_key: API key for Grok (xAI)
            serpapi_key: API key for SerpAPI
            silence_timeout: Seconds of silence before responding
            max_response_words: Maximum words in response (unless 'explain')
            explain_keyword: Keyword that allows longer responses
            elevenlabs_api_key: API key for ElevenLabs (optional, for better TTS)
            elevenlabs_voice_id: Voice ID for ElevenLabs (default: Rachel)
            use_elevenlabs: Whether to use ElevenLabs for TTS (True) or system say (False)
        """
        self.grok_api_key = grok_api_key
        self.grok_api_url = "https://api.x.ai/v1/chat/completions"  # xAI Grok API endpoint
        self.serpapi_key = serpapi_key
        self.silence_timeout = silence_timeout
        self.max_response_words = max_response_words
        self.explain_keyword = explain_keyword.lower()
        
        # ElevenLabs TTS configuration
        self.elevenlabs_api_key = elevenlabs_api_key
        self.elevenlabs_voice_id = elevenlabs_voice_id
        self.use_elevenlabs = use_elevenlabs and elevenlabs_api_key is not None
        self.elevenlabs_available = False
        self.elevenlabs_generate = None
        self.elevenlabs_play = None
        self.elevenlabs_set_api_key = None
        
        # Try to import ElevenLabs
        if self.use_elevenlabs:
            try:
                from elevenlabs import generate, play, set_api_key
                self.elevenlabs_generate = generate
                self.elevenlabs_play = play
                self.elevenlabs_set_api_key = set_api_key
                self.elevenlabs_available = True
                set_api_key(elevenlabs_api_key)
                logger.info("✅ ElevenLabs TTS enabled")
            except ImportError:
                self.elevenlabs_available = False
                self.use_elevenlabs = False
                logger.warning("⚠️  ElevenLabs not installed. Install with: pip install elevenlabs")
                logger.info("ℹ️  Falling back to system TTS (say command)")
            except Exception as e:
                self.elevenlabs_available = False
                self.use_elevenlabs = False
                logger.error(f"❌ ElevenLabs initialization error: {e}")
                logger.info("ℹ️  Falling back to system TTS (say command)")
        else:
            logger.info("ℹ️  Using system TTS (say command) - ElevenLabs API key not provided")
        
        # Audio components - REQUIRED for voice chat
        self.audio_available = AUDIO_AVAILABLE
        if not self.audio_available:
            raise RuntimeError(
                "Audio support is required for voice chat. "
                "Install PyAudio: brew install portaudio && pip install pyaudio"
            )
        
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000  # Adjust for ambient noise
            self.recognizer.pause_threshold = 0.8
            self.microphone = sr.Microphone()
            # Calibrate microphone
            logger.info("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            logger.info("Audio initialized successfully")
        except Exception as e:
            logger.error(f"Audio initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize audio: {e}") from e
        
        self.speaking = False
        self.interrupt_speech = False
        self.speech_thread: Optional[threading.Thread] = None
        self.background_listener_stop = None  # Function to stop background listener
        
        # State management
        self.is_listening = False
        self.last_audio_time = None
        self.audio_queue = Queue()
        self.violations = []
    
    def _detect_english_input(self, audio_data) -> Optional[str]:
        """Detect if audio contains English speech."""
        if not self.audio_available or not self.recognizer:
            return None
        try:
            text = self.recognizer.recognize_google(audio_data, language='en-US')
            if text:
                logger.info(f"Detected English input: {text}")
                return text
        except Exception as e:
            if self.audio_available and sr:
                if isinstance(e, sr.UnknownValueError):
                    pass  # Could not understand audio
                elif isinstance(e, sr.RequestError):
                    logger.warning(f"Speech recognition error: {e}")
                else:
                    logger.warning(f"Audio detection error: {e}")
            else:
                logger.warning(f"Audio detection error: {e}")
        return None
    
    def _interruption_callback(self, recognizer, audio):
        """
        Callback function for background listener - called when audio is detected.
        This is the proper way to detect interruptions in speech_recognition.
        """
        if not self.speaking or self.interrupt_speech:
            return  # Already interrupted or not speaking
        
        try:
            logger.info("🔊 Audio detected during speech - checking for interruption...")
            # Try to recognize the audio
            try:
                english_text = recognizer.recognize_google(audio, language='en-US')
                if english_text and len(english_text.strip()) > 0:
                    self.interrupt_speech = True
                    logger.info(f"🚨 INTERRUPTED by user: '{english_text}'")
                    self._log_violation(f"Speech interrupted by user input: {english_text}")
            except sr.UnknownValueError:
                # Couldn't understand, but audio was detected - treat as interruption anyway
                logger.info("🚨 INTERRUPTED: Audio detected (could not transcribe - treating as interruption)")
                self.interrupt_speech = True
                self._log_violation("Speech interrupted by audio detection (untranscribable)")
            except sr.RequestError as e:
                # Service error, but audio was detected - treat as interruption
                logger.info(f"🚨 INTERRUPTED: Audio detected (recognition service error: {e})")
                self.interrupt_speech = True
                self._log_violation("Speech interrupted by audio detection (recognition error)")
        except Exception as e:
            logger.warning(f"Interruption callback error: {e}")
            # Still treat as interruption if audio was detected
            self.interrupt_speech = True
    
    def _start_interruption_detection(self):
        """
        Start background listening for interruptions using listen_in_background.
        This is the proper way to continuously listen while speaking.
        """
        if not self.audio_available or not self.speaking:
            return
        
        try:
            logger.info("🎤 Starting background interruption detection...")
            
            # Use the existing recognizer and microphone, but adjust for sensitivity
            interrupt_recognizer = sr.Recognizer()
            interrupt_recognizer.energy_threshold = 2000  # More sensitive
            interrupt_recognizer.pause_threshold = 0.3  # Shorter pause
            interrupt_recognizer.dynamic_energy_threshold = True
            
            # Adjust for ambient noise quickly
            with self.microphone as source:
                interrupt_recognizer.adjust_for_ambient_noise(source, duration=0.2)
            
            logger.info(f"🎤 Interruption detection ready (energy_threshold={interrupt_recognizer.energy_threshold})")
            
            # Start background listener with callback
            # phrase_time_limit=1.0 means accept 1 second of speech as interruption
            self.background_listener_stop = interrupt_recognizer.listen_in_background(
                self.microphone,
                self._interruption_callback,
                phrase_time_limit=1.0  # Accept 1 second of speech as valid interruption
            )
            logger.info("✅ Background interruption listener started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start interruption detection: {e}")
            # Continue anyway - TTS will still check self.interrupt_speech flag
    
    def _wait_for_silence(self) -> bool:
        """
        Wait for silence timeout before processing/responding.
        Returns True if silence detected, False if interrupted.
        """
        logger.debug(f"Waiting {self.silence_timeout}s for silence...")
        start_time = time.time()
        while time.time() - start_time < self.silence_timeout:
            if self.interrupt_speech:
                logger.info("Silence wait interrupted")
                return False
            time.sleep(0.1)
        
        logger.debug("Silence timeout reached")
        return True
    
    def _search_web(self, query: str) -> Optional[str]:
        """Search web using SerpAPI for factual claims. Returns comprehensive context."""
        if GoogleSearch is None:
            logger.warning("SerpAPI not available. Web search disabled.")
            self._log_violation("Web search attempted but SerpAPI not installed")
            return None
        
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 3  # Get top 3 results for richer context
            })
            results = search.get_dict()
            
            # Combine top results for better context
            context_parts = []
            
            # Check for answer box or knowledge graph (direct answers)
            if "answer_box" in results and results["answer_box"]:
                answer = results["answer_box"].get("answer", "") or results["answer_box"].get("snippet", "")
                if answer:
                    logger.info("Web search found direct answer box")
                    context_parts.append(f"Direct answer: {answer}")
            
            # Extract top 3 organic results for comprehensive context
            if "organic_results" in results and len(results["organic_results"]) > 0:
                for i, result in enumerate(results["organic_results"][:3]):
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    if snippet:
                        context_parts.append(f"{title}: {snippet}")
                
                if context_parts:
                    # Combine multiple results for richer context
                    combined_context = " | ".join(context_parts)
                    logger.info(f"Web search provided {len(results['organic_results'][:3])} results ({len(combined_context)} chars)")
                    return combined_context
            
            logger.warning(f"No search results for: {query}")
            return None
        except Exception as e:
            logger.error(f"SerpAPI search error: {e}")
            self._log_violation(f"Web search failed: {str(e)}")
            return None
    
    def _extract_factual_claims(self, text: str) -> List[str]:
        """Extract potential factual claims from text."""
        # Simple pattern matching for factual claims
        # Look for statements that might need verification
        patterns = [
            r'\b\d{4}\b',  # Years
            r'\b(is|was|are|were)\s+\w+',  # "is/was" statements
            r'\b(according to|studies show|research indicates)',
            r'\b(percent|percentage|\%)',
        ]
        
        claims = []
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            for pattern in patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence.strip())
                    break
        
        return claims
    
    def _query_grok(self, user_input: str, context: Optional[str] = None) -> str:
        """Query Grok API using requests."""
        # Validate API key first
        if not self.grok_api_key or self.grok_api_key in ["your-grok-api-key-here", ""]:
            error_msg = "Error: Grok API key not set. Edit .env file and add your API key from https://console.x.ai"
            logger.error(error_msg)
            self._log_violation("Grok API key not configured")
            return error_msg
        
        try:
            messages = []
            # Enhanced system prompt optimized for high-quality, informative answers (matches web app quality)
            system_prompt = """You are Grok, an advanced AI assistant created by xAI. 
Your goal is to provide accurate, insightful, and helpful answers that demonstrate deep understanding.

Quality guidelines:
- Provide detailed, well-reasoned answers that show you understand the topic thoroughly
- When web search context is provided, use it to give current, factual, and accurate information
- Be thorough but clear - explain concepts with relevant details and context
- If asked to explain something, provide comprehensive information with examples when helpful
- Be conversational, natural, and engaging - write like you're helping a friend understand
- If uncertain about something, acknowledge it rather than speculating
- When using information from web search, synthesize it naturally into a coherent answer
- Prioritize accuracy, helpfulness, and completeness
- Think through your answers before responding to ensure quality"""
            
            # Build context-rich messages - format web search context clearly
            if context:
                # Format context clearly so model can use it effectively (clear separation helps)
                messages.append({
                    "role": "system",
                    "content": system_prompt + f"\n\n=== Current Web Search Context (use this to inform your answer) ===\n{context}\n=== End of Web Search Context ===\n\nUse this context to provide an accurate, detailed, and helpful answer. Synthesize the information naturally into your response."
                })
            else:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            logger.debug(f"Sending to Grok: {len(messages)} messages, context: {bool(context)}")
            
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Querying Grok API at {self.grok_api_url} with {len(messages)} messages")
            
            # Try common Grok model names (grok-3 is the current model)
            model_names = ["grok-3", "grok-beta", "grok-2", "grok-vision-beta", "grok"]
            last_response = None
            
            for model_name in model_names:
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": 0.7,  # Balanced - good for factual, thoughtful answers (was 0.8)
                    "max_tokens": 2000,  # Increased significantly for comprehensive, detailed answers (was 1000)
                    "top_p": 0.9,  # Balanced nucleus sampling for quality (was 0.95)
                    "frequency_penalty": 0.0,  # Don't penalize repetition (allows better explanations)
                    "presence_penalty": 0.0,  # Don't penalize new topics
                }
                
                response = requests.post(
                    self.grok_api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                last_response = response
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully using model: {model_name}")
                    return result["choices"][0]["message"]["content"]
                elif response.status_code == 400:
                    # Check if it's a model error or API key error
                    error_text = response.text.lower()
                    if "model" in error_text and ("invalid" in error_text or "not found" in error_text):
                        # Try next model
                        logger.debug(f"Model {model_name} not available, trying next...")
                        continue
                    else:
                        # Likely API key error or other issue
                        break
            
            # If we get here, all models failed or it's an API key issue
            if last_response:
                logger.error(f"Grok API error: {last_response.status_code} - {last_response.text}")
                self._log_violation(f"Grok API error: {last_response.status_code}")
                
                error_text = last_response.text.lower()
                
                # Check API key validity (partial mask for security)
                api_key_preview = self.grok_api_key[:5] + "..." if len(self.grok_api_key) > 10 else "***"
                if self.grok_api_key == "your-grok-api-key-here" or "your-grok-api-key" in self.grok_api_key.lower():
                    return "Error: Grok API key not set. Edit .env file and add your API key from https://console.x.ai"
                
                if last_response.status_code == 401 or "api key" in error_text or "unauthorized" in error_text:
                    return f"Error: Invalid Grok API key ({api_key_preview}). Get a valid key from https://console.x.ai"
                elif last_response.status_code == 400:
                    # Try to parse JSON error for more details
                    try:
                        error_json = last_response.json()
                        error_msg = error_json.get("error", {}).get("error", "Invalid request")
                        return f"Error: {error_msg}. Check API key and model availability."
                    except:
                        return f"Error: Invalid request (400). Response: {last_response.text[:200]}"
                elif last_response.status_code == 404:
                    return f"Error: API endpoint not found. URL: {self.grok_api_url}"
                elif last_response.status_code == 429:
                    return "Error: Rate limit exceeded. Wait a moment and try again."
                else:
                    return f"Error: Grok API returned {last_response.status_code}: {last_response.text[:200]}"
            
            return "Error: Could not get response from Grok (no response received)"
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Error: Cannot connect to Grok API at {self.grok_api_url}. Check your internet connection."
            logger.error(f"Grok API connection error: {e}")
            self._log_violation(f"Grok API connection error: {str(e)}")
            return error_msg
        except requests.exceptions.Timeout as e:
            error_msg = "Error: Grok API request timed out. The service may be slow or unavailable."
            logger.error(f"Grok API timeout: {e}")
            self._log_violation(f"Grok API timeout: {str(e)}")
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Error: Network error connecting to Grok API: {str(e)}"
            logger.error(f"Grok API request error: {e}")
            self._log_violation(f"Grok API request error: {str(e)}")
            return error_msg
        except Exception as e:
            error_msg = f"Error: Unexpected error with Grok API: {type(e).__name__}: {str(e)}"
            logger.error(f"Grok API unexpected error: {e}", exc_info=True)
            self._log_violation(f"Grok API unexpected error: {type(e).__name__}: {str(e)}")
            return error_msg
    
    def _limit_response_length(self, response: str, user_input: str) -> str:
        """Limit response to max words unless 'explain' keyword present."""
        user_input_lower = user_input.lower()
        
        # Check for 'explain' keyword - allows full response
        if self.explain_keyword in user_input_lower:
            logger.info(f"'explain' keyword detected, allowing full response")
            return response
        
        # Smart truncation: Try to end at sentence boundary instead of mid-word
        words = response.split()
        if len(words) > self.max_response_words:
            # Try to truncate at sentence boundary (period, exclamation, question mark)
            truncated_words = words[:self.max_response_words]
            truncated = ' '.join(truncated_words)
            
            # Check if we're cutting mid-sentence - if so, look for punctuation before truncation point
            original_truncated = truncated
            for i in range(min(self.max_response_words, len(words)) - 1, max(0, self.max_response_words - 5), -1):
                if words[i][-1] in '.!?':
                    truncated = ' '.join(words[:i+1])
                    logger.info(f"Truncated at sentence boundary: {i+1} words")
                    break
            
            # If still too long or no sentence boundary found, use original truncation
            if len(truncated.split()) > self.max_response_words:
                truncated = original_truncated
                # Add ellipsis if cut mid-sentence
                if truncated[-1] not in '.!?':
                    truncated += '...'
            
            logger.info(f"Truncated response from {len(words)} to {len(truncated.split())} words")
            self._log_violation(f"Response truncated: {len(words)} words -> {len(truncated.split())} words")
            return truncated
        
        return response
    
    def _speak_text(self, text: str, callback: Optional[Callable] = None):
        """Speak text using TTS, interruptible by English input."""
        self.speaking = True
        self.interrupt_speech = False
        
        def speak():
            try:
                # Start background interruption detection (uses listen_in_background)
                self._start_interruption_detection()
                
                # Wait a moment for background listener to start
                time.sleep(0.2)
                
                # Use ElevenLabs if available, otherwise fall back to system say
                if self.use_elevenlabs and self.elevenlabs_available:
                    try:
                        logger.info(f"🔊 Speaking with ElevenLabs (voice: {self.elevenlabs_voice_id})...")
                        # Generate audio with ElevenLabs in a thread so we can check for interruption
                        audio_generated = threading.Event()
                        audio_data = None
                        audio_error = None
                        
                        def generate_audio():
                            nonlocal audio_data, audio_error
                            try:
                                audio_data = self.elevenlabs_generate(
                                    text=text,
                                    voice=self.elevenlabs_voice_id,
                                    model="eleven_monolingual_v1"
                                )
                                audio_generated.set()
                            except Exception as e:
                                audio_error = e
                                audio_generated.set()
                        
                        # Generate audio in background
                        gen_thread = threading.Thread(target=generate_audio, daemon=True)
                        gen_thread.start()
                        
                        # Wait for audio generation with interruption check
                        while not audio_generated.is_set():
                            if self.interrupt_speech:
                                logger.info("🚨 Speech interrupted during ElevenLabs generation")
                                break
                            time.sleep(0.1)
                        
                        if audio_error:
                            raise audio_error
                        
                        if not self.interrupt_speech and audio_data:
                            # Play audio using ElevenLabs play (plays through speakers)
                            # Note: This is less interruptible, but sounds much better
                            logger.info("🎵 Playing ElevenLabs audio...")
                            self.elevenlabs_play(audio_data)
                            
                            if self.interrupt_speech:
                                logger.info("🚨 ElevenLabs TTS was interrupted")
                    except Exception as e:
                        logger.error(f"❌ ElevenLabs TTS error: {e}")
                        logger.info("ℹ️  Falling back to system TTS")
                        # Fall through to system TTS
                        self.use_elevenlabs = False
                
                # System TTS (fallback or if ElevenLabs not used)
                if not self.use_elevenlabs or not self.elevenlabs_available:
                    logger.info("🔊 Speaking with system TTS (say command)...")
                    words = text.split()
                    chunk_size = 5  # Speak in small chunks for interruption
                    
                    for i in range(0, len(words), chunk_size):
                        # Check for interruption before speaking each chunk
                        if self.interrupt_speech:
                            logger.info("🚨 Speech interrupted, stopping TTS immediately")
                            # Kill all say processes immediately
                            try:
                                subprocess.run(['pkill', '-9', 'say'], check=False, timeout=0.5)
                                subprocess.run(['killall', '-9', 'say'], check=False, timeout=0.5)
                            except:
                                pass
                            break
                        
                        chunk = ' '.join(words[i:i+chunk_size])
                        try:
                            # Start say process
                            proc = subprocess.Popen(['say', chunk], 
                                                  stdout=subprocess.DEVNULL, 
                                                  stderr=subprocess.DEVNULL)
                            
                            # Check periodically while speaking this chunk
                            chunk_start = time.time()
                            while proc.poll() is None:  # Process still running
                                if self.interrupt_speech:
                                    logger.info("🚨 Interruption detected during chunk, killing say process")
                                    proc.kill()
                                    subprocess.run(['pkill', '-9', 'say'], check=False, timeout=0.5)
                                    break
                                if time.time() - chunk_start > 3:  # Safety timeout
                                    proc.kill()
                                    break
                                time.sleep(0.1)  # Check every 100ms
                            
                            # Wait for process to finish if not interrupted
                            if not self.interrupt_speech:
                                proc.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            subprocess.run(['pkill', '-9', 'say'], check=False)
                        except Exception as e:
                            logger.debug(f"TTS chunk error: {e}")
                        
                        if self.interrupt_speech:
                            break
                
                self.speaking = False
                
                # Stop background listener
                if self.background_listener_stop:
                    try:
                        self.background_listener_stop(wait_for_stop=False)
                        logger.info("✅ Stopped background interruption listener")
                    except Exception as e:
                        logger.debug(f"Error stopping background listener: {e}")
                    self.background_listener_stop = None
                
                if callback:
                    callback()
            except Exception as e:
                logger.error(f"TTS error: {e}")
                self.speaking = False
                
                # Stop background listener on error
                if self.background_listener_stop:
                    try:
                        self.background_listener_stop(wait_for_stop=False)
                    except:
                        pass
                    self.background_listener_stop = None
                
                if callback:
                    callback()
        
        self.speech_thread = threading.Thread(target=speak, daemon=True)
        self.speech_thread.start()
    
    def _log_violation(self, message: str):
        """Log a violation."""
        violation = {
            'timestamp': time.time(),
            'message': message
        }
        self.violations.append(violation)
        logger.warning(f"VIOLATION: {message}")
    
    def process_input(self, user_input: str) -> str:
        """
        Main method to process user input with all constraints.
        
        Args:
            user_input: User's text input
            
        Returns:
            Response string
        """
        # Step 1: Wait for silence detection
        if not self._wait_for_silence():
            self._log_violation("Response generated without silence timeout")
            return "Interrupted"
        
        # Step 2: Extract factual claims and search web for better context
        claims = self._extract_factual_claims(user_input)
        search_context = None
        
        # Always search web for better context - helps improve answer quality significantly
        if claims:
            logger.info(f"Found {len(claims)} potential factual claims")
            # Search for first claim with more detail
            search_query = claims[0][:150]  # Longer query for better search results
            search_context = self._search_web(search_query)
        else:
            # Search for general context - helps even for non-factual questions
            search_query = user_input[:150]
            logger.info(f"Searching web for context: {search_query}")
            search_context = self._search_web(search_query)
        
        if search_context:
            logger.info(f"Web search provided context ({len(search_context)} chars)")
        else:
            logger.info("No web search context available - proceeding without it")
        
        # Step 3: Query Grok with context
        response = self._query_grok(user_input, search_context)
        
        # Step 4: Limit response length unless 'explain'
        response = self._limit_response_length(response, user_input)
        
        return response
    
    def start_listening(self):
        """Start background listening for interruption detection while speaking."""
        # No persistent listener needed - will start when speaking
        pass
    
    def stop_listening(self):
        """Stop any active listening."""
        self.is_listening = False
        logger.info("Stopped listening")
    
    def speak(self, text: str):
        """Speak text (can be interrupted by live listening)."""
        self._speak_text(text)
    
    def get_violations(self) -> List[Dict]:
        """Get all logged violations."""
        return self.violations.copy()
    
    def clear_violations(self):
        """Clear violation log."""
        self.violations.clear()
        logger.info("Violations log cleared")
    
    def _listen_and_transcribe(self, timeout: float = 5.0, phrase_time_limit: float = 10.0) -> Optional[str]:
        """
        Listen to microphone and transcribe speech to text.
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time to listen for phrase
            
        Returns:
            Transcribed text or None if no speech detected
        """
        try:
            with self.microphone as source:
                logger.info("Listening...")
                # Adjust for ambient noise before each listen
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Recognize speech
            logger.info("Processing speech...")
            text = self.recognizer.recognize_google(audio, language='en-US')
            logger.info(f"Heard: {text}")
            return text
        except sr.WaitTimeoutError:
            logger.debug("No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error listening: {e}")
            return None
    
    def voice_chat(self, exit_phrases: List[str] = None):
        """
        Start a continuous voice chat session.
        
        Args:
            exit_phrases: List of phrases that will exit the chat (default: ['exit', 'goodbye', 'quit'])
        """
        if exit_phrases is None:
            exit_phrases = ['exit', 'goodbye', 'quit', 'stop', 'end']
        
        exit_phrases_lower = [phrase.lower() for phrase in exit_phrases]
        
        logger.info("=== Starting Voice Chat ===")
        logger.info(f"Say one of {exit_phrases} to exit")
        
        try:
            while True:
                # Wait for initial silence (ensures we're ready for new input)
                if not self._wait_for_silence():
                    continue
                
                # Listen and transcribe (this detects silence internally via phrase_time_limit)
                # SpeechRecognition automatically detects end of speech (silence)
                user_input = self._listen_and_transcribe(timeout=5.0, phrase_time_limit=15.0)
                
                if not user_input:
                    continue
                
                # Additional silence wait after input (as per requirement: "respond only after silence detection")
                logger.debug("Waiting for silence after input before processing...")
                time.sleep(self.silence_timeout)
                
                # Check for exit phrases
                if user_input.lower() in exit_phrases_lower:
                    logger.info("Exit phrase detected. Ending voice chat.")
                    self.speak("Goodbye!")
                    break
                
                # Process input with all constraints
                logger.info(f"Processing: {user_input}")
                response = self.process_input(user_input)
                
                # Speak response (interruption detection starts automatically)
                if response and response != "Interrupted":
                    logger.info(f"Response: {response}")
                    self.speak(response)
                    
                    # Wait for speech to finish (unless interrupted)
                    if self.speech_thread and self.speech_thread.is_alive():
                        self.speech_thread.join(timeout=30)
                
        except KeyboardInterrupt:
            logger.info("Voice chat interrupted by user")
        except Exception as e:
            logger.error(f"Voice chat error: {e}")
            self._log_violation(f"Voice chat error: {str(e)}")
        finally:
            self.stop_listening()
            self.speaking = False
            logger.info("=== Voice Chat Ended ===")
    
    def process_voice_input(self) -> Optional[str]:
        """
        Listen to voice input, process it, and return response (text only, no speaking).
        Useful for testing or custom response handling.
        
        Returns:
            Response text or None if no input detected
        """
        # Wait for silence
        if not self._wait_for_silence():
            return None
        
        # Listen and transcribe
        user_input = self._listen_and_transcribe()
        
        if not user_input:
            return None
        
        # Process input
        response = self.process_input(user_input)
        return response

