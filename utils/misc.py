import pandas as pd
from recommend.models import DietPlan
import os

def request_image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_assets/<profile_id>/profile_image/<filename>
    return "{0}/{1}/{2}/{3}".format(
        "user_assets", instance.user.username, "requests_image", filename
    )


def save_diets_from_excel():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    xlsx_file_path = os.path.join(current_directory, "diets.xlsx")
    
    # xlsx_file_path = "./diets.xlsx"
    data = pd.read_excel(xlsx_file_path)

    for _, row in data.iterrows():
        DietPlan.objects.create(
            day=row["Day"], time=row["Time"], meal=row["Meal"], body_type=row["Type"]
        )
