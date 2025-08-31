import streamlit as st
import base64
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Floratrack Survey App",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'About': "The Floratrack Survey App prototype for detecting Rhodesian Teak."},
)

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)

st.markdown("""
<style>
:root {
    --primary-green: #28a745;
    --light-green: #e9f7ee;
    --accent-green: #4CAF50;
    --dark-green: #1e7e34;
    --text-dark: #333333;
    --text-light: #666666;
    --border-light: #d4edda;
    --shadow-color: rgba(0, 0, 0, 0.1);
    --hero-bg: #dff0d8;
}
html, body {
    margin: 0 !important;
    padding: 0 !important;
    height: 100% !important;
    width: 100% !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: var(--text-dark);
    background-color: var(--light-green) !important;
    background-image: linear-gradient(135deg, #e9f7ee 0%, #daf2e4 100%) !important;
    background-attachment: fixed !important;
    overflow-x: hidden;
}
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    min-height: 100vh !important;
    width: 100% !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
}
[data-testid="stAppViewContainer"] > div:first-child {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
[role="main"] > .block-container {
    max-width: 750px !important;
    margin: 0px auto !important;
    background-color: #ffffff !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 30px var(--shadow-color) !important;
    padding: 0px !important;
    box-sizing: border-box !important;
    border: 1px solid var(--border-light) !important;
    width: calc(100% - 80px) !important;
    flex-shrink: 0;
}
[data-testid="stAppViewContainer"] > div > [data-testid="stVerticalBlock"] {
    background-color: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}
header, [data-testid="stToolbar"], .st-emotion-cache-s8e469 {
    display: none !important;
    visibility: hidden !important;
    width: 0px !important;
    height: 0px !important;
    overflow: hidden !important;
}
.hero-section {
    text-align: center;
    padding: 10px;
    background-color: var(--hero-bg);
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    border: 1px solid var(--primary-green);
}
.hero-section h3 {
    color: var(--dark-green);
    font-size: 1.5em;
    margin-bottom: 5px;
    font-weight: 700;
}
.hero-section p {
    font-size: 1.2em;
    color: var(--text-light);
    line-height: 1.7;
    max-width: 800px;
    margin: 0 auto;
}
.hero-section strong { color: var(--primary-green); }
h1 {
    color: var(--dark-green);
    text-align: center;
    margin-top: 0px !important;
    margin-bottom: 30px;
    font-size: 3em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
}
h1 .icon {
    margin-right: 20px;
    font-size: 1.3em;
    color: var(--primary-green);
}
h2 {
    color: var(--accent-green);
    border-bottom: 3px solid var(--border-light);
    padding-bottom: 15px;
    margin-top: 45px;
    margin-bottom: 30px;
    font-size: 2.2em;
    font-weight: 600;
}
h3 {
    color: var(--dark-green);
    font-size: 1.7em;
    margin-top: 30px;
    margin-bottom: 20px;
    font-weight: 600;
}
.stButton>button {
    background-color: var(--white);
    color: primary-green;
    border-radius: 10px;
    border: none;
    padding: 14px 30px;
    font-size: 1.25em;
    font-weight: bold;
    transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
    box-shadow: 0 6px 15px rgba(0,0,0,0.25);
    width: 100%;
    margin-top: 25px;
    letter-spacing: 0.5px;
}
.stButton>button:hover {
    background-color: var(--white);
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}
.stButton>button:active {
    transform: translateY(0);
    box-shadow: 0 3px 8px rgba(0,0,0,0.2);
}
.stFileUploader label {
    color: var(--accent-green);
    font-size: 1.3em;
    font-weight: bold;
    margin-bottom: 12px;
    display: block;
}
.stFileUploader section {
    border: 3px dashed var(--primary-green);
    border-radius: 12px;
    padding: 30px;
    background-color: #fafffc;
    transition: border-color 0.3s ease, background-color 0.3s ease;
    text-align: center;
    margin-bottom: 20px;
}
.stFileUploader section:hover {
    border-color: var(--dark-green);
    background-color: #f7fff7;
}
.stFileUploader p {
    color: var(--text-light);
    font-size: 1.1em;
}
.stAlert {
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 25px;
    font-size: 1.1em;
    border-left: 8px solid;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.stAlert.success { background-color: #d4edda; color: #155724; border-color: #28a745; }
.stAlert.info { background-color: #d1ecf1; color: #0c5460; border-color: #17a2b8; }
.stAlert.error { background-color: #f8d7da; color: #721c24; border-color: #dc3545; }
img {
    border-radius: 15px;
    max-width: 100%;
    height: auto;
    display: block;
    margin-left: auto;
    margin-right: auto;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    margin-top: 30px;
    border: 2px solid var(--border-light);
}
hr { border-top: 3px dashed var(--border-light); margin-top: 50px; margin-bottom: 50px; }
pre code {
    background-color: #f8f8f8;
    border-radius: 10px;
    padding: 20px;
    border: 1px solid #e5e5e5;
    white-space: pre-wrap;
    word-break: break-all;
    font-size: 0.95em;
}
[data-testid="stMetric"] {
    background-color: #f0fff0;
    border: 1px solid var(--border-light);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    transition: transform 0.2s ease;
}
[data-testid="stMetric"]:hover { transform: translateY(-5px); }
[data-testid="stMetric"] label {
    color: var(--accent-green);
    font-weight: bold;
    font-size: 1.15em;
    margin-bottom: 5px;
}
[data-testid="stMetric"] div {
    color: var(--dark-green);
    font-size: 2em;
    font-weight: bold;
    margin-top: 8px;
}
.stSpinner > div > div { color: var(--primary-green) !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1><span class='icon'><i class='fas fa-leaf'></i></span> Floratrack Survey App</h1>", unsafe_allow_html=True)

st.markdown("""
<div class="hero-section">
    <h3>Empowering Citizen Scientists for Conservation</h3>
    <p>Join us in identifying and tracking the vital Rhodesian Teak Tree (Baikiaea plurijuga). Simply upload an image and let our AI do the rest!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

status_message_placeholder = st.empty()
loading_placeholder = st.empty()

response_data_str = st.query_params.get('data')

if response_data_str:
    try:
        response_data = json.loads(response_data_str)
        loading_placeholder.empty()
        message_from_js = response_data.get('message', "No message received.")
        type_from_js = response_data.get('type', "info")
        gps_data_from_js = response_data.get('gps')
        st.markdown("---")
        if type_from_js == "success":
            st.subheader("✅ AI Detection & Location Captured!")
            st.success("Your tree image has been successfully processed, and location data is recorded. Thank you for your contribution!")
            with st.expander("✨ View AI Model Response (Technical Details)"):
                st.code(message_from_js, language='json')
            st.markdown("---")
            st.subheader("What's Next for Your Contribution?")
            st.write("Your valuable data point helps us in monitoring and conservation of Rhodesian Teak populations. Consider submitting more images!")
        elif type_from_js == "error":
            st.subheader("❌ Oops! Something Went Wrong During Processing.")
            st.error(message_from_js)
            st.write("Please check your internet connection, location permissions, and image validity, then try again.")
            if st.button("Retry Detection", key="retry_button"):
                st.query_params.clear()
                st.rerun()
    except json.JSONDecodeError:
        st.error("Error processing response from backend. Data may be corrupted.")
    st.stop()

uploaded_file = st.file_uploader(
    "Drag and drop an image file here or click to browse",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False,
    key="file_uploader"
)

if uploaded_file is not None:
    st.subheader("🖼️ Your Uploaded Image Preview:")
    st.image(uploaded_file, caption='Photo successfully loaded.', use_container_width=True)
    status_message_placeholder.success("Image received! Now, click 'Detect & Capture Location' to analyze.")

    encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    image_mime_type = uploaded_file.type

    st.markdown("---")
    st.header("📍 Detect & Locate Tree")
    st.write("Click the button below to send your image to our AI model and capture your GPS location.")
    st.info("💡 **Important:** Please allow location access in your browser when prompted.")

    if st.button("🚀 Detect Tree & Capture Location", key="detect_button_main"):
        status_message_placeholder.empty()
        loading_placeholder.info("⏳ Getting location and sending image to AI for analysis...")
        js_code = f"""
        async function runDetection() {{
            const API_URL = 'http://127.0.0.1:8000/api/detect-plant';
            if (navigator.geolocation) {{
                try {{
                    const position = await new Promise((resolve, reject) => {{
                        navigator.geolocation.getCurrentPosition(resolve, reject, {{enableHighAccuracy: true, timeout: 15000, maximumAge: 0}});
                    }});
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    const byteCharacters = atob("{encoded_image}");
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {{
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }}
                    const byteArray = new Uint8Array(byteNumbers);
                    const imageBlob = new Blob([byteArray], {{ type: "{image_mime_type}" }});
                    const formData = new FormData();
                    formData.append('image', imageBlob, '{uploaded_file.name}');
                    formData.append('latitude', latitude);
                    formData.append('longitude', longitude);
                    const response = await fetch(API_URL, {{ method: 'POST', body: formData }});
                    if (!response.ok) {{
                        const errorText = await response.text();
                        throw new Error(`API request failed: ${{response.status}} - ${{errorText}}`);
                    }}
                    const result = await response.json();
                    const responseData = {{ message: JSON.stringify(result, null, 2), type: "success", gps: {{ latitude, longitude, accuracy }} }};
                    const encodedData = encodeURIComponent(JSON.stringify(responseData));
                    window.location.href = `/?data=${{encodedData}}`;
                }} catch (error) {{
                    let errorMessage = "Geolocation error: ";
                    switch(error.code) {{
                        case 1: errorMessage = "User denied location access."; break;
                        case 2: errorMessage = "Location unavailable."; break;
                        case 3: errorMessage = "Request timed out."; break;
                        default: errorMessage = "Unknown error during detection.";
                    }}
                    const errorData = {{ message: errorMessage, type: "error" }};
                    const encodedData = encodeURIComponent(JSON.stringify(errorData));
                    window.location.href = `/?data=${{encodedData}}`;
                }}
            }} else {{
                const errorData = {{ message: "Geolocation not supported.", type: "error" }};
                const encodedData = encodeURIComponent(JSON.stringify(errorData));
                window.location.href = `/?data=${{encodedData}}`;
            }}
        }}
        runDetection();
        """
        components.html(f"<script>{js_code}</script>", height=0, width=0, scrolling=False)

st.markdown("""
<div style="text-align: center; padding-top: 40px; color: var(--text-light); font-size: 0.9em;">
    &copy; 2025 Floratrack Survey Prototype by Unearth the Wild Team.<br>
    Built with love, for conservation. ❤️
</div>
""", unsafe_allow_html=True)
