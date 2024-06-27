
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from Class.Imo import ImoAPI

import json

app = Flask(__name__)
route_base = "/imo"
CORS(app, resources={r"/*": {"origins": "*"}}, headers='Content-Type')

@app.route(route_base + "/process-cms-report-monitoring", methods=["GET"])
def StartMonitoring():
    excludedImoIdsStr = None
    excluded_imo_ids = request.args.get("excluded_imo_ids")
    if excluded_imo_ids:
        excludedImoIdsArr = json.loads(excluded_imo_ids)
        excludedImoIdsStr = ', '.join(str(x) for x in excludedImoIdsArr)
    imoInstance = ImoAPI()
    result = imoInstance.StartMonitoring(excludedImoIdsStr)
    return make_response(jsonify(result), 200)

@app.route(route_base + "/check-fuel-consumption", methods=["GET"])
def CheckFuelConsumption():
    imoInstance = ImoAPI()
    result = imoInstance.CheckFuelConsumption()
    return make_response(jsonify(result), 200)

if __name__ == "__main__":
    app.run(debug=True)

# from Class.Imo import ImoAPI

# def StartMonitoring():
#     imoInstance = ImoAPI()
#     return imoInstance.StartMonitoring()

# def TestEmail(email):
#     imoInstance = ImoAPI()
#     return imoInstance.SendEmail(email)

# result = TestEmail("eduardo@offshoredoneright.com")
# print(result)
    