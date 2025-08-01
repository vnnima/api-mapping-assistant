# Trade Protect - API Mapping Assistant

## How to Run This App

Follow these steps to get the application running locally.

### 1. Prerequisites

*   Python 3.8+
*   An [OpenAI API Key](https://platform.openai.com/api-keys).

### 2. Setup

**Step 1: Get the Code**

Clone this repository or download the `app.py` file to a new project directory.

```bash
git clone <repository_url>
cd <repository_name>
```

**Step 2: Create a `requirements.txt` file**

Create a file named `requirements.txt` in your project directory and add the following lines:

```
streamlit
openai
python-dotenv
```

**Step 3: Install Dependencies**

Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

**Step 4: Configure Your OpenAI API Key**

This app uses Streamlit's secrets management.

1.  Create a folder named `.streamlit` in your project's root directory.
2.  Inside the `.streamlit` folder, create a file named `secrets.toml`.

Your project structure should look like this:

```
your-project/
├── .streamlit/
│   └── secrets.toml
└── app.py
```

3.  Add your OpenAI API key to the `secrets.toml` file:

    ```toml
    # .streamlit/secrets.toml
    OPENAI_API_KEY = "sk-your-secret-key-goes-here"
    ```

    **Important:** Replace `"sk-your-secret-key-goes-here"` with your actual OpenAI API key.

### 3. Run the Application

Navigate to your project directory in the terminal and run the following command:

```bash
streamlit run app.py
```

Your web browser should automatically open with the application running.