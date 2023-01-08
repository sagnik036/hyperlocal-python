from base.utils import get_file_from_url


def save_user_image(backend, user, response, *args, **kwargs):
    if backend.name == "facebook":
        image_url = response['picture']['data']['url']
        fb_id = response['id']
        user.username = fb_id
        extension, file = get_file_from_url(image_url)
        user.profile_picture.save(f"image{extension}", file, save=False)
        user.save()
