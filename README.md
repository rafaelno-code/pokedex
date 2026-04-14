# Pokedex

A simple Flask-based Python web application.

---

## Setup

Install the required dependencies before running the application:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the Flask server by running the following command in the project directory:

```bash
python app.py
```

The server will start locally at:

```text
http://127.0.0.1:5000
```

---

## Testing Endpoints

To test an endpoint, open a **separate terminal** and use `curl`:

```bash
curl http://127.0.0.1:5000/{endpoint}
```

Replace `{endpoint}` with the endpoint you want to test.

### Example

```bash
curl http://127.0.0.1:5000/hello
```

---

## Current Status

- One endpoint is currently implemented.
- Additional endpoints can be tested using the same curl format as they are added.