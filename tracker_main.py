import math

class EuclideanDistTracker:
    def __init__(self):
        # Store the positions and size of the objects
        self.vehicle_points = {}
        # Store frame_usage of the objects
        self.vehicle_frame_usage = {}
        # Store the speed of the objects
        self.vehicle_speeds = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0
        self.s_id_count = 0
        self.m_id_count = 0
        self.l_id_count = 0

    def update(self, objects_rect, iframe, fps):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.vehicle_points.items():
                x_pt, y_pt, w_pt, h_pt, is_count = pt
                cx_pt = (x_pt + x_pt + w_pt) // 2
                cy_pt = (y_pt + y_pt + h_pt) // 2

                iframe_pt, _ = self.vehicle_frame_usage[id]

                dist = math.hypot(cx - cx_pt, cy - cy_pt)

                # validate new car
                t = 5
                if dist < 390 and x_pt - t < cx < x_pt + w_pt + t:

                    if (w_pt * h_pt) * 0.5 > w * h:
                        x, y, w, h = x_pt, y_pt, w_pt, h_pt

                    if cy < 350 and is_count == False:
                        is_count = True
                        if w <= 150:
                            self.s_id_count += 1
                        elif w <= 310:
                            self.m_id_count += 1
                        else:
                            self.l_id_count += 1

                        t = (iframe - iframe_pt) / fps
                        v = (4.5 / t) * 3.6 # 4.4m
                        self.vehicle_speeds[id] = "{:.2f}".format(v)
                        iframe_pt = iframe

                    self.vehicle_points[id] = (x, y, w, h, is_count)
                    self.vehicle_frame_usage[id] = (iframe_pt, iframe)
                    objects_bbs_ids.append([x, y, w, h, id, is_count])
                    same_object_detected = True
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False and cy > 400:
                self.id_count += 1
                self.vehicle_points[self.id_count] = (x, y, w, h, False)
                self.vehicle_frame_usage[self.id_count] = (iframe, None)
                self.vehicle_speeds[self.id_count] = None
                objects_bbs_ids.append([x, y, w, h, self.id_count, False])

        # Clean the dictionary by center points to remove IDS not used anymore
        new_vehicle_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id, _ = obj_bb_id
            vehicle_point = self.vehicle_points[object_id]
            new_vehicle_points[object_id] = vehicle_point

        # Update dictionary with IDs not used removed
        self.vehicle_points = new_vehicle_points.copy()
        return {
            'objects_bbs_ids': objects_bbs_ids,
            'total': self.id_count,
            's_total': self.s_id_count,
            'm_total': self.m_id_count,
            'l_total': self.l_id_count,
            'speeds': self.vehicle_speeds
        }
