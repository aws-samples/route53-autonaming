from flask import Flask, jsonify, render_template
import socket
import requests
import boto3
app = Flask(__name__)

servicediscovery = boto3.client("servicediscovery")

@app.route("/ping")
def ping():
    return "", 200

def discover_frosting_api():
    print ("Get from r53")

def dbaas_ec2_api():
    print ("query from r53")

@app.route("/")
def cakecrusts():
    return jsonify({'CakeCrustTypes': ['VanillaCrust', 'ChocolateCrust', 'StrawberryCrust']})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')