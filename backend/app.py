from fastapi import FastAPI
from starlette.responses import JSONResponse

from backend.auth.api import router as auth_router
from backend.core import settings
from backend.core.middleware import add_process_time_header, set_session


app = FastAPI(debug=settings.DEBUG)

app.middleware('http')(add_process_time_header)
app.middleware('http')(set_session)


@app.route('/ping/', methods=['GET'], include_in_schema=False)
async def health_check():
    return JSONResponse({'status': 'ok'})


app.include_router(auth_router)
