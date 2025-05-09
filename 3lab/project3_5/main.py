import uvicorn
import celery
# celery -A app.clr.celery_app worker --pool=eventlet --loglevel=info
if __name__ == "__main__":
    uvicorn.run("project3_5.app.serv.logic:app", host="127.0.0.1", port=8000)
