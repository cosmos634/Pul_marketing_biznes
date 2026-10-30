from pathlib import Path
from datetime import datetime
import json
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
Path(app.instance_path).mkdir(parents=True, exist_ok=True)
app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///" + str(Path(app.instance_path) / "academy.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY="local-biznes-akademiya"
)
db = SQLAlchemy(app)

class Module(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(140),nullable=False)
    description=db.Column(db.Text,default="")
    icon=db.Column(db.String(12),default="📘")
    lessons=db.relationship("Lesson",backref="module",cascade="all,delete-orphan",order_by="Lesson.day")

class Lesson(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    day=db.Column(db.Integer,unique=True,nullable=False)
    module_id=db.Column(db.Integer,db.ForeignKey("module.id"),nullable=False)
    title=db.Column(db.String(180),nullable=False)
    summary=db.Column(db.Text,default="")
    theory=db.Column(db.Text,default="")
    example=db.Column(db.Text,default="")
    visual=db.Column(db.Text,default="")
    task=db.Column(db.Text,default="")
    case_study=db.Column(db.Text,default="")
    takeaways=db.Column(db.Text,default="[]")

class Progress(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    day=db.Column(db.Integer,unique=True,nullable=False)
    completed=db.Column(db.Boolean,default=False)
    score=db.Column(db.Integer,default=0)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

class Question(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    day=db.Column(db.Integer,nullable=False)
    prompt=db.Column(db.Text,nullable=False)
    options=db.Column(db.Text,nullable=False)
    answer=db.Column(db.Integer,nullable=False)
    explanation=db.Column(db.Text,default="")

class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    day=db.Column(db.Integer,nullable=False)
    body=db.Column(db.Text,default="")
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

class Bookmark(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    day=db.Column(db.Integer,unique=True,nullable=False)

def lesson_json(lesson):
    p=Progress.query.filter_by(day=lesson.day).first()
    n=Note.query.filter_by(day=lesson.day).first()
    return {"day":lesson.day,"title":lesson.title,"summary":lesson.summary,"theory":lesson.theory,
      "example":lesson.example,"visual":lesson.visual,"task":lesson.task,"case_study":lesson.case_study,
      "takeaways":json.loads(lesson.takeaways or "[]"),"completed":bool(p and p.completed),
      "score":p.score if p else 0,"note":n.body if n else "",
      "bookmarked":Bookmark.query.filter_by(day=lesson.day).first() is not None}

@app.get("/")
def index():
    modules=Module.query.order_by(Module.id).all()
    lessons=Lesson.query.order_by(Lesson.day).all()
    done=Progress.query.filter_by(completed=True).count()
    current=next((x.day for x in lessons if not Progress.query.filter_by(day=x.day,completed=True).first()),30)
    return render_template("index.html",modules=modules,lessons=lessons,done=done,current=current)

@app.get("/api/lesson/<int:day>")
def get_lesson(day):
    lesson=Lesson.query.filter_by(day=day).first_or_404()
    data=lesson_json(lesson)
    data["questions"]=[{"id":q.id,"prompt":q.prompt,"options":json.loads(q.options)}
                       for q in Question.query.filter_by(day=day).all()]
    return jsonify(data)

@app.post("/api/quiz/<int:day>")
def quiz(day):
    payload=request.get_json(silent=True) or {}
    answers=payload.get("answers",{})
    questions=Question.query.filter_by(day=day).all()
    if not questions: return jsonify({"error":"Test topilmadi"}),404
    correct=0; details=[]
    for q in questions:
        choice=answers.get(str(q.id))
        ok=isinstance(choice,int) and choice==q.answer
        correct+=int(ok)
        details.append({"id":q.id,"correct":ok,"answer":q.answer,"explanation":q.explanation})
    score=round(correct/len(questions)*100)
    p=Progress.query.filter_by(day=day).first()
    if not p: p=Progress(day=day); db.session.add(p)
    p.score=max(p.score or 0,score)
    if score>=60: p.completed=True
    db.session.commit()
    return jsonify({"correct":correct,"total":len(questions),"score":score,"passed":score>=60,"details":details})

@app.post("/api/note/<int:day>")
def save_note(day):
    body=(request.get_json(silent=True) or {}).get("body","")
    if not isinstance(body,str) or len(body)>10000: return jsonify({"error":"Qayd 10 000 belgidan oshmasin"}),400
    n=Note.query.filter_by(day=day).first()
    if not n: n=Note(day=day); db.session.add(n)
    n.body=body; db.session.commit()
    return jsonify({"saved":True})

@app.post("/api/bookmark/<int:day>")
def bookmark(day):
    b=Bookmark.query.filter_by(day=day).first()
    if b: db.session.delete(b); saved=False
    else: db.session.add(Bookmark(day=day)); saved=True
    db.session.commit()
    return jsonify({"saved":saved})

@app.get("/api/search")
def search():
    q=request.args.get("q","").strip()[:100]
    if not q: return jsonify([])
    rows=Lesson.query.filter((Lesson.title.ilike(f"%{q}%"))|(Lesson.summary.ilike(f"%{q}%"))).order_by(Lesson.day).all()
    return jsonify([{"day":x.day,"title":x.title,"summary":x.summary} for x in rows])

@app.get("/api/export")
def export_data():
    return jsonify({"progress":[{"day":p.day,"completed":p.completed,"score":p.score} for p in Progress.query.all()],
      "notes":[{"day":n.day,"body":n.body} for n in Note.query.all()],
      "bookmarks":[b.day for b in Bookmark.query.all()]})

@app.post("/api/import")
def import_data():
    data=request.get_json(silent=True) or {}
    try:
        for x in data.get("progress",[]):
            day=int(x["day"])
            if 1<=day<=30:
                p=Progress.query.filter_by(day=day).first() or Progress(day=day)
                p.completed=bool(x.get("completed")); p.score=max(0,min(100,int(x.get("score",0))))
                db.session.add(p)
        for x in data.get("notes",[]):
            day=int(x["day"])
            if 1<=day<=30 and isinstance(x.get("body"),str):
                n=Note.query.filter_by(day=day).first() or Note(day=day)
                n.body=x["body"][:10000]; db.session.add(n)
        for day in data.get("bookmarks",[]):
            day=int(day)
            if 1<=day<=30 and not Bookmark.query.filter_by(day=day).first(): db.session.add(Bookmark(day=day))
        db.session.commit()
        return jsonify({"imported":True})
    except (ValueError,KeyError,TypeError):
        db.session.rollback()
        return jsonify({"error":"JSON fayl formati noto‘g‘ri"}),400

with app.app_context():
    db.create_all()
    from seed import seed
    seed()

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=True)
