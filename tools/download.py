#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
from overture_song.model import ApiConfig, Manifest, ManifestEntry, SongError
from overture_song.client import Api, ManifestClient, StudyClient
from overture_song.tools import FileUploadClient
from overture_song.utils import setup_output_file_path
import subprocess
import requests


def create_manifest(api, analysis_id, payload_file, manifest_file,files_dir):
    payload = json.load(open(payload_file))

    with open(os.path.join(files_dir,manifest_file), 'w') as outfile:
        outfile.write(analysis_id+'\t\t\n')
        for i in range(0,len(payload.get('file'))):
            file_object = payload.get('file')[i]
            outfile.write(retrieve_object_id(api,analysis_id,
                                             file_object.get('fileName'),
                                             file_object.get('fileMd5sum'))+'\t'+os.path.join(files_dir,file_object.get('fileName'))+'\t'+file_object.get('fileMd5sum')+'\n')
    return

def retrieve_object_id(api, analysis_id, file_name, file_md5sum):
    analysis = api.get_analysis(analysis_id).__dict__
    for file in analysis.get('file'):
        if file.__dict__.get('fileName') == file_name and file.__dict__.get('fileMd5sum') == file_md5sum:
            return file.__dict__.get('objectId')
    raise Exception('The object id could not be found for '+file_name)


def upload_payload(api, payload_file):
    api_upload = api.upload(json.load(open(payload_file)))
    upload_status = api.status(api_upload.uploadId)

    if not upload_status.state == 'VALIDATED':
        raise Exception("Song upload could not be validated - Analysis id "+upload_status.analysisId+", Current State: "+upload_status.state)
    return upload_status

def validate_payload_against_analysis(api,analysis_id, payload_file):
    json_data = json.load(open(payload_file))
    payload_files = []
    for file in json_data.get('file'):
        payload_files.append(file)

    for file in api.get_analysis_files(analysis_id):
        tmp_file = {'fileName':file.fileName,'fileSize':file.fileSize,'fileType':file.fileType,'fileMd5sum':file.fileMd5sum,'fileAccess':file.fileAccess}
        if not tmp_file in payload_files:
            raise Exception("The payload to be uploaded and the analysis on SONG do not match.")
    return True

def main():
    parser = argparse.ArgumentParser(description='Download using manifest')
    #parser.add_argument('-s', '--study-id', dest="study_id", help="Study ID", required=True)
    #parser.add_argument('-u', '--server-url', dest="server_url", help="Server URL", required=True)
    #parser.add_argument('-p', '--payload', dest="payload", help="JSON Payload", required=True)
    parser.add_argument('-m', '--manifest', dest="manifest", help="manifest file", required=True)
    #parser.add_argument('-o', '--output', dest="output", help="Output manifest file", required=True)
    parser.add_argument('-d', '--input-dir', dest="input_dir", help="Payload files directory", required=True)
    parser.add_argument('-t', '--access-token', dest="access_token", default=os.environ.get('ACCESSTOKEN',None),help="Server URL")
    parser.add_argument('-o','--output-dir',dest="output_dir")
    results = parser.parse_args()

    #study_id = results.study_id
    #server_url = results.server_url
    access_token = results.access_token
    manifest = results.manifest
    output_dir = results.output_dir
    #analysis_id = json.load(open(payload_file)).get('analysisId')
   

    subprocess.check_output(['/home/hnahal/score-client-5.1.0/bin/score-client','--profile', 'collab', 'download','--manifest',os.path.join(results.input_dir,manifest) , '--output-dir', os.path.join(output_dir)])

if __name__ == "__main__":
    main()
