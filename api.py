from flask import Flask, request, jsonify
from utils import main, convert_sets_to_lists

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_news():
    
    data = request.get_json()

    # Check if 'company' is present
    if not data or "company" not in data:
        return jsonify({"error": "Missing 'company' in request body"}), 400

    company = data["company"]
    try:
        # 'main()' from utils.py is called
        result = main(company)
        
        # function from the utils file
        result = convert_sets_to_lists(result)  
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
