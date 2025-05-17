from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# DB 연결
print('DB 연결중')
MONGO_URI = "mongodb://admin:admin@124.49.102.176:27011"
client = MongoClient(MONGO_URI)
db = client.dbjungle
collection = db.memos
print('DB 연결 설정 완료')


@app.route('/')
def render_page():
    return render_template('index.html')


# ObjectId 처리
def serialize_memo(memo):
    return {
        "id": str(memo["_id"]),
        "title": memo["title"],
        "content": memo["content"],
        "likes": memo.get("likes", 0)
    }


# 메모 전체 처리
@app.route("/list/memos", methods=["GET"])
def get_memos():
    memos = list(collection.find())
    return jsonify([serialize_memo(m) for m in memos])


# 메모 포스트
@app.route("/upload/memos", methods=["POST"])
def post_memo():
    data = request.get_json()
    memo = {
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "likes": 0
    }
    result = collection.insert_one(memo)
    return jsonify({"result": "success", "id": str(result.inserted_id)})


# 좋아요 처리
@app.route("/memos/<memo_id>/like", methods=["POST"])
def like_memo(memo_id):
    collection.update_one({"_id": ObjectId(memo_id)}, {"$inc": {"likes": 1}})
    return jsonify({"result": "liked"})


# 수정 처리
@app.route("/memos/edit/<memo_id>", methods=["POST"])
def update_memo(memo_id):
    data = request.get_json()
    collection.update_one(
        {"_id": ObjectId(memo_id)},
        {"$set": {"title": data["title"], "content": data["content"]}}
    )
    return jsonify({"result": "updated"})


# 메모 지우기
@app.route("/memos/del/<memo_id>", methods=["POST"])
def delete_memo(memo_id):
    collection.delete_one({"_id": ObjectId(memo_id)})
    return jsonify({"result": "deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
