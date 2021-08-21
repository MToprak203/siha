# Kamera değerlerini tutar.

v_path = "Tools/Video/aeroplane.mp4" # Kamera için 0, video için "adres"
cam_width = 640
cam_height = 480

min_target_width = int(cam_width / 20)
min_target_height = int(cam_height / 20)

center_point = (cam_width / 2, cam_height / 2)
target_view_size = (cam_width / 2, cam_height * 4 / 5)

target_hit_area = (cam_width / 4, cam_height / 10, cam_width / 2, cam_height * 4 / 5)  # x1, y1, w, h
hit_area_points = (cam_width / 4, cam_height / 10, cam_width * 3 / 4, cam_height * 9 / 10)  # x1, y1, x2, y2