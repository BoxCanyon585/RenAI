/**
 * AudioManager - Handles voice recording and text-to-speech playback
 */
class AudioManager {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.currentAudio = null; // For TTS playback
    }

    /**
     * Start recording audio from microphone
     */
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            // Use webm format with opus codec (widely supported)
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : 'audio/webm';

            this.mediaRecorder = new MediaRecorder(stream, { mimeType });
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.start();
            this.isRecording = true;

            console.log('Recording started');
        } catch (error) {
            console.error('Error starting recording:', error);

            // Provide user-friendly error message
            if (error.name === 'NotAllowedError') {
                throw new Error('Microphone permission denied. Please allow microphone access in your browser settings.');
            } else if (error.name === 'NotFoundError') {
                throw new Error('No microphone found. Please connect a microphone and try again.');
            } else {
                throw new Error(`Failed to access microphone: ${error.message}`);
            }
        }
    }

    /**
     * Stop recording and return the audio blob
     */
    async stopRecording() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder || !this.isRecording) {
                reject(new Error('Not currently recording'));
                return;
            }

            this.mediaRecorder.onstop = async () => {
                // Stop all tracks
                if (this.mediaRecorder.stream) {
                    this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
                }

                // Create blob from recorded chunks
                const audioBlob = new Blob(this.audioChunks, { type: this.mediaRecorder.mimeType });
                this.isRecording = false;

                console.log(`Recording stopped. Size: ${audioBlob.size} bytes`);
                resolve(audioBlob);
            };

            this.mediaRecorder.stop();
        });
    }

    /**
     * Send audio to backend for transcription
     */
    async transcribeAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const response = await fetch('/api/stt/transcribe', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Transcription failed');
            }

            const data = await response.json();
            return data.text || '';
        } catch (error) {
            console.error('Transcription error:', error);
            throw new Error(`Failed to transcribe audio: ${error.message}`);
        }
    }

    /**
     * Play text as speech using TTS
     */
    async playTextAsSpeech(text) {
        if (!text || text.trim().length === 0) {
            console.warn('Cannot play empty text');
            return;
        }

        try {
            // Stop any currently playing audio
            this.stopPlayback();

            const response = await fetch('/api/tts/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'TTS synthesis failed');
            }

            // Get audio blob
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);

            // Create and play audio
            this.currentAudio = new Audio(audioUrl);

            // Clean up URL when done
            this.currentAudio.onended = () => {
                URL.revokeObjectURL(audioUrl);
                this.currentAudio = null;
            };

            await this.currentAudio.play();
            console.log('Playing TTS audio');
        } catch (error) {
            console.error('TTS playback error:', error);
            throw new Error(`Failed to play speech: ${error.message}`);
        }
    }

    /**
     * Stop currently playing TTS audio
     */
    stopPlayback() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio = null;
        }
    }

    /**
     * Check if audio is currently playing
     */
    isPlaying() {
        return this.currentAudio && !this.currentAudio.paused;
    }

    /**
     * Cancel ongoing recording
     */
    cancelRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            if (this.mediaRecorder.stream) {
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            this.audioChunks = [];
            this.isRecording = false;
        }
    }
}
