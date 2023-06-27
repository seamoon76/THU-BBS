from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from db_dependencies import schemas, crud
from fastapi.responses import FileResponse
import snowflake.client
from init_parameters import host, port, snowflake_port, snowflake_host
from moviepy.editor import VideoFileClip
import asyncio, os, shutil

get_db = crud.get_db

router = APIRouter(
    prefix='/resource',
    tags=['resource'],
)

async def process_video(id, sfx):
    input_file = 'resource/' + '{}.{}'.format(id, sfx)
    output_file = 'resource/' + 'zipped_{}.{}'.format(id, sfx)
    clip = VideoFileClip(input_file)
    clip.write_videofile(output_file, bitrate='1M')
    shutil.copy2(output_file, input_file)

@router.post('/upload', response_model=schemas.UploadResourceResponse)
async def upload_file(file: UploadFile= File(...)):
    snowflake.client.setup(snowflake_host, snowflake_port)
    file_id = snowflake.client.get_guid()
    file_sfx = file.filename.split('.')[-1]
    file_name = '{}.{}'.format(file_id, file_sfx)
    file_path = 'resource/'

    try:
        res = await file.read()
        with open(file_path + file_name, "wb") as f:
            f.write(res)
        if file_sfx == 'mp4':
            #asyncio.create_task(process_video(file_id, file_sfx))
            pass
    except:
        raise HTTPException(400, detail='Upload Failed')
        
    return {'url': '{}:{}/resource/{}'.format(host, port, file_name)}


@router.get('/{filename}')
async def download_file(filename: str):
    try:
        res = FileResponse('./resource/'+filename, filename=filename)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail='Error')
    except RuntimeError:
        raise HTTPException(status_code=400, detail='Error')
    return res
