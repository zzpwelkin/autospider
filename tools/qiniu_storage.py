#-*- encoding:utf8 -*-
from qiniu import Auth, put_data, build_batch_delete
from qiniu import BucketManager
from bson import MAX_INT64

class QiniuError(Exception):
    name='qiniuerror'
    pass

class QiniuPushDataError(QiniuError):
    name = 'qiniuppushdataerror'
    
class QiniuReadDataError(QiniuError):
    name = 'qiniuppushdataerror'
    
def auth(ak, sk):
    return Auth(ak, sk)

class QiniuBucketManager:
    def __init__(self, auth, bucket):
        """
        @param auth: qiniu auth object
        @param bucket: bucket name
        """
        self.auth = auth
        self.bucket = bucket
        self.bktmanager = BucketManager(auth)

        self.upload_token = auth.upload_token(bucket)
        
    def data_info(self, key):
        """
        return information with keys {fsize, hash, mimetype, putTime} else
        raise  `QiniuReadDataError` with status_code and error message
        """
        r, info = self.bktmanager.stat(self.bucket, key)
        if not r:
            raise QiniuReadDataError('status_code:{0}, error:{1}'.format(info.status_code,
                            info.text_body))
        else:
            return r
    
    def push_data(self, key, data):
        """
        return hash code if upload sucess else raise `QiniuPushDataError` 
        with status_code and error message
        """
        ret, info = put_data(self.upload_token, key, data)
        if not ret:
            raise QiniuPushDataError('status_code:{0}, error:{1}'.format(info.status_code,
                            info.text_body))
        else:
            return ret['hash']
    
    def delete_data(self, key):
        """
        delete data `key`
        """
        _, info = self.bktmanager.delete(self.bucket, key)
        if info.status_code != 200:
            raise QiniuError('status_code:{0}, error:{1}'.format(info.status_code,
                            info.text_body))
    
    def batch_delete_data(self, keys):
        if keys:
            ops = build_batch_delete(self.bucket, keys)
            _, info = self.bktmanager.batch(ops)
            if info.status_code != 200:
                msg = ''
                for e in info.text_body:
                    msg += msg + ';' + 'status_code:{0}, error:{1}'.format(e)
                raise QiniuError(msg)
        
    def copy_data_to(self, sdata, dbucket, ddata):
        """
        copy data `sdata` in this bucket to destination bucket `dbucket` with name `ddata`
        """
        _, info = self.bktmanager.copy(self.bucket, sdata, dbucket, ddata)
        if info.status_code != 200:
            raise QiniuError('status_code:{0}, error:{1}'.format(info.status_code,
                            info.text_body))
    
    def copy_data_from(self, sbucket, sdata, ddata):
        """
        copy data from `sdata` in bucket `sbucket` to this bucket with name `ddata`
        """
        _, info = self.bktmanager.copy(sbucket, sdata, self.bucket, ddata)
        if info.status_code != 200:
            raise QiniuError('status_code:{0}, error:{1}'.format(info.status_code,
                            info.text_body))
    
    def move_data_to(self, sdata, dbucket, ddata):
        """
        move data `sdata` in this bucket to destination bucket `dbucket` with name `ddata`
        """
        _, info = self.bktmanager.move(self.bucket, sdata, dbucket, ddata)
        if info.status_code != 200:
            raise QiniuError('status_code:{0}, error:{1}'.format(info.status_code,
                            info.text_body))
    
    def move_data_from(self, sbucket, sdata, ddata):
        """
        move data from `sdata` in bucket `sbucket` to this bucket with name `ddata`
        """
        _, info = self.bktmanager.move(sbucket, sdata, self.bucket, ddata)
        if info.status_code != 200:
            raise QiniuError('status_code:{0}, error:{1}'.format(info.status_code,
                            info.text_body))
    
    def datas(self, prefix=None, limit=None, marker=None):
        """
        list datas in bucket with keys fsize, hash, key, mimeType, puttime of each data 
        """
        def list_files(marker, limit):
            k = {'bucket':self.bucket}
            if limit:
                k['limit'] = limit
            if prefix:
                k['prefix'] = prefix
            if marker:
                k['marker'] = marker
            return  self.bktmanager.list(**k)

        eof = False
        res = []
        mk = marker
        lm = limit if limit else MAX_INT64
        while not eof and lm:
            _r, eof, info = list_files(mk, lm)
            if info.status_code != 200:
                raise QiniuError('status_code:{0}, error:{1}'.format(info.status_code,
                            info.text_body))
                
            mk = _r.get('marker', None)
            lm = lm-len(_r['items'])
            res += _r['items']
        return res
    
if __name__ == "__main__":
    qiniu_access_key = 'gtkn1Qwp4rFLAu37ewAleGOuDZpdAFhf36Nc4c47'
    qiniu_secret_key = 'O7K3gvDSB59opFnlwv3PMFirPoYelMhg3WuZqjGA'
    qiniu_bucket = 'newcarspicture'
    
    qm = QiniuBucketManager(auth(qiniu_access_key, qiniu_secret_key), qiniu_bucket)
    #qm.push_data('data_test', 'nihao')
    
    dt = qm.datas(limit=1)
    dt = qm.datas()
    
    tmp_dt = [d['key'].encode('utf8') for d in dt]
    print len(tmp_dt)
    
#     qm.delete_data(tmp_dt[0])
#     qm.batch_delete_data(tmp_dt[1:])