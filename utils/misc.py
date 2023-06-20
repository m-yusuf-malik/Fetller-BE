def request_image_directory_path(instance, filename):

    # file will be uploaded to MEDIA_ROOT/user_assets/<profile_id>/profile_image/<filename>
    return '{0}/{1}/{2}/{3}'.format('user_assets', instance.user.username, 'requests_image', filename)
