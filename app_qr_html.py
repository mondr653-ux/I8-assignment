from flask import Flask
import json

app = Flask(__name__)

with open("food_safety_data.json") as f:
    data = json.load(f)

records   = data["safety_records"]
nutrition = data["nutrition"]


@app.route('/')
def info():
    return '''
<!DOCTYPE html>
<html>
<head>
  <title>QR Food Safety API</title>
  <style>
    body { font-family: sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; }
    h1 { font-size: 24px; }
    h2 { font-size: 16px; color: #555; margin-top: 32px; }
    a  { display: block; padding: 8px 12px; margin: 6px 0; background: #f5f5f5;
         border-radius: 6px; text-decoration: none; color: #111; font-family: monospace; }
    a:hover { background: #e8e8e8; }
  </style>
</head>
<body>
  <h1>🥗 QR Food Safety Inspector API</h1>
  <h2>Safety Records</h2>
  <a href="/api/v1/records/QR-CHICKEN-001-A">/api/v1/records/QR-CHICKEN-001-A</a>
  <a href="/api/v1/records/QR-SALMON-002-B">/api/v1/records/QR-SALMON-002-B</a>
  <a href="/api/v1/records/QR-BEEF-005-E">/api/v1/records/QR-BEEF-005-E</a>
  <h2>Sub-routes (replace QR code ID)</h2>
  <a href="/api/v1/records/QR-CHICKEN-001-A/status">/api/v1/records/&lt;id&gt;/status</a>
  <a href="/api/v1/records/QR-CHICKEN-001-A/recall">/api/v1/records/&lt;id&gt;/recall</a>
  <a href="/api/v1/records/QR-CHICKEN-001-A/allergens">/api/v1/records/&lt;id&gt;/allergens</a>
  <a href="/api/v1/records/QR-CHICKEN-001-A/supply">/api/v1/records/&lt;id&gt;/supply</a>
  <h2>Nutrition</h2>
  <a href="/api/v1/nutrition/food/Banana">/api/v1/nutrition/food/Banana</a>
  <a href="/api/v1/nutrition/meal/Breakfast">/api/v1/nutrition/meal/Breakfast</a>
  <a href="/api/v1/nutrition/category/Fruit">/api/v1/nutrition/category/Fruit</a>
</body>
</html>
'''


@app.route('/api/v1/records/<qr_id>')
def get_record(qr_id):
    if qr_id not in records:
        return '<h2>QR code not found: ' + qr_id + '</h2>', 404
    r = records[qr_id]
    p = r["product_identifier"]
    s = r["safety_and_quality_information"]
    rc = r["recall_information"]
    sc = r["supply_chain_information"]

    status_color = "#2e7d32" if s["inspection_status"] == "passed" else "#c62828"
    recall_color = "#c62828" if rc["recall_status"] == "active" else "#2e7d32"

    steps_html = ""
    for step in sc["processing_steps"]:
        steps_html += f'<li><strong>{step["step_name"]}</strong> — {step["location"]} <span style="color:#888">({step["step_date"][:10]})</span></li>'

    allergens_html = ""
    for a in s["allergen_info"]:
        allergens_html += f'<li>{a["allergen_name"]} — risk: <strong>{a["allergen_risk"]}</strong></li>'

    recall_note = ""
    if rc["recall_status"] == "active":
        recall_note = f'<p style="background:#fff3f3;border-left:4px solid #c62828;padding:10px 14px;border-radius:4px;color:#c62828"><strong>⚠ Active Recall:</strong> {rc.get("recall_reason", "")}</p>'

    return f'''
<!DOCTYPE html>
<html>
<head>
  <title>{p["product_name"]}</title>
  <style>
    body {{ font-family: sans-serif; max-width: 680px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ font-size: 22px; margin-bottom: 4px; }}
    .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px;
              font-size: 13px; font-weight: bold; color: #fff; margin-bottom: 20px; }}
    h2 {{ font-size: 15px; color: #555; margin-top: 28px; border-bottom: 1px solid #eee; padding-bottom: 6px; }}
    table {{ width: 100%; font-size: 14px; border-collapse: collapse; }}
    td {{ padding: 6px 4px; border-bottom: 1px solid #f0f0f0; }}
    td:first-child {{ color: #666; width: 40%; }}
    ul {{ font-size: 14px; line-height: 2; padding-left: 18px; }}
    a {{ font-size: 13px; color: #1565c0; }}
  </style>
</head>
<body>
  <a href="/">← back</a>
  <h1>{p["product_name"]}</h1>
  <span class="badge" style="background:{status_color}">Inspection: {s["inspection_status"].upper()}</span>
  &nbsp;
  <span class="badge" style="background:{recall_color}">Recall: {rc["recall_status"].upper()}</span>

  {recall_note}

  <h2>Product</h2>
  <table>
    <tr><td>Brand</td><td>{p["brand_name"]}</td></tr>
    <tr><td>GTIN</td><td>{p["gtin"]}</td></tr>
    <tr><td>Batch ID</td><td>{p["batch_id"]}</td></tr>
    <tr><td>Expires</td><td>{p["expiration_date"][:10]}</td></tr>
  </table>

  <h2>Supply chain</h2>
  <p style="font-size:14px;color:#555">Origin: {sc["origin_location"]}</p>
  <ul>{steps_html}</ul>

  <h2>Safety &amp; quality</h2>
  <table>
    <tr><td>Inspection date</td><td>{s["inspection_date"][:10]}</td></tr>
    <tr><td>Temperature control</td><td>{s["temperature_control_status"]}</td></tr>
  </table>
  <ul>{allergens_html}</ul>

  <p style="font-size:12px;color:#aaa;margin-top:32px">Last updated: {r["last_updated"]}</p>
</body>
</html>
'''


@app.route('/api/v1/records/<qr_id>/status')
def get_status(qr_id):
    if qr_id not in records:
        return 'not found', 404
    r = records[qr_id]
    return json.dumps({
        "product_name":      r["product_identifier"]["product_name"],
        "inspection_status": r["safety_and_quality_information"]["inspection_status"],
        "recall_status":     r["recall_information"]["recall_status"],
        "recall_risk_level": r["recall_information"]["recall_risk_level"],
        "last_updated":      r["last_updated"]
    }, indent=2)


@app.route('/api/v1/records/<qr_id>/recall')
def get_recall(qr_id):
    if qr_id not in records:
        return 'not found', 404
    return json.dumps(records[qr_id]["recall_information"], indent=2)


@app.route('/api/v1/records/<qr_id>/allergens')
def get_allergens(qr_id):
    if qr_id not in records:
        return 'not found', 404
    r = records[qr_id]
    return json.dumps({
        "product_name":  r["product_identifier"]["product_name"],
        "allergen_info": r["safety_and_quality_information"]["allergen_info"]
    }, indent=2)


@app.route('/api/v1/records/<qr_id>/supply')
def get_supply(qr_id):
    if qr_id not in records:
        return 'not found', 404
    return json.dumps(records[qr_id]["supply_chain_information"], indent=2)


@app.route('/api/v1/nutrition/food/<food_item>')
def get_nutrition(food_item):
    for item in nutrition:
        if item['Food_Item'].lower() == food_item.lower():
            rows = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in item.items())
            return f'''
<!DOCTYPE html><html><head><title>{item["Food_Item"]}</title>
<style>body{{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}}
h1{{font-size:20px}}table{{width:100%;font-size:14px;border-collapse:collapse}}
td{{padding:6px 4px;border-bottom:1px solid #f0f0f0}}td:first-child{{color:#666;width:55%}}
a{{font-size:13px;color:#1565c0}}</style></head>
<body><a href="/">← back</a><h1>{item["Food_Item"]}</h1><table>{rows}</table></body></html>'''
    return 'Food item not found: ' + food_item, 404


@app.route('/api/v1/nutrition/meal/<meal_type>')
def get_by_meal(meal_type):
    results = [i for i in nutrition if i['Meal_Type'].lower() == meal_type.lower()]
    if not results:
        return 'No items for meal type: ' + meal_type, 404
    rows = "".join(
        f'<tr><td><a href="/api/v1/nutrition/food/{i["Food_Item"]}">{i["Food_Item"]}</a></td>'
        f'<td>{i["Category"]}</td><td>{i["Calories (kcal)"]} kcal</td></tr>'
        for i in results
    )
    return f'''
<!DOCTYPE html><html><head><title>{meal_type}</title>
<style>body{{font-family:sans-serif;max-width:680px;margin:40px auto;padding:0 20px}}
h1{{font-size:20px}}table{{width:100%;font-size:14px;border-collapse:collapse}}
th{{text-align:left;padding:8px 4px;border-bottom:2px solid #eee;color:#555}}
td{{padding:6px 4px;border-bottom:1px solid #f0f0f0}}
a{{color:#1565c0;text-decoration:none}}a:hover{{text-decoration:underline}}</style></head>
<body><a href="/">← back</a><h1>{meal_type} — {len(results)} items</h1>
<table><tr><th>Food item</th><th>Category</th><th>Calories</th></tr>{rows}</table></body></html>'''


@app.route('/api/v1/nutrition/category/<category>')
def get_by_category(category):
    results = [i for i in nutrition if i['Category'].lower() == category.lower()]
    if not results:
        return 'No items for category: ' + category, 404
    rows = "".join(
        f'<tr><td><a href="/api/v1/nutrition/food/{i["Food_Item"]}">{i["Food_Item"]}</a></td>'
        f'<td>{i["Meal_Type"]}</td><td>{i["Calories (kcal)"]} kcal</td>'
        f'<td>{i["Protein (g)"]}g</td><td>{i["Fat (g)"]}g</td></tr>'
        for i in results
    )
    return f'''
<!DOCTYPE html><html><head><title>{category}</title>
<style>body{{font-family:sans-serif;max-width:680px;margin:40px auto;padding:0 20px}}
h1{{font-size:20px}}table{{width:100%;font-size:14px;border-collapse:collapse}}
th{{text-align:left;padding:8px 4px;border-bottom:2px solid #eee;color:#555}}
td{{padding:6px 4px;border-bottom:1px solid #f0f0f0}}
a{{color:#1565c0;text-decoration:none}}a:hover{{text-decoration:underline}}</style></head>
<body><a href="/">← back</a><h1>{category} — {len(results)} items</h1>
<table><tr><th>Food item</th><th>Meal type</th><th>Calories</th><th>Protein</th><th>Fat</th></tr>{rows}</table></body></html>'''


if __name__ == '__main__':
    app.run(debug=True)
