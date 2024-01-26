import hashlib

class HashUtil():
    
    @staticmethod
    def hash_data(data, algorithm='sha1'):

        if algorithm == 'sha1':
            hasher = hashlib.sha1()
        # Add other hashing algorithms if needed

        hasher.update(data.encode('utf-8'))
        hash_result = hasher.hexdigest()
        return hash_result