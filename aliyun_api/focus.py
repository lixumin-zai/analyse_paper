# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :



def get_rect_iou(rec1, rec2):
    """
    computing IoU
    :param rec1: (y0, x0, y1, x1), which reflects
        (top, left, bottom, right)
    :param rec2: (y0, x0, y1, x1)
    :return: scala value of IoU
    """
    # computing area of each rectangles
    S_rec1 = (rec1[2] - rec1[0]) * (rec1[3] - rec1[1])
    S_rec2 = (rec2[2] - rec2[0]) * (rec2[3] - rec2[1])

    # computing the sum_area
    sum_area = S_rec1 + S_rec2

    # find the each edge of intersect rectangle
    left_line = max(rec1[1], rec2[1])
    right_line = min(rec1[3], rec2[3])
    top_line = max(rec1[0], rec2[0])
    bottom_line = min(rec1[2], rec2[2])

    # judge if there is an intersect
    if left_line >= right_line or top_line >= bottom_line:
        return 0
    else:
        intersect = (right_line - left_line) * (bottom_line - top_line)
        return (intersect / (sum_area - intersect)) * 1.0

def get_focus(resp_teacher, resp_student):
    focus_list = []
    img_x = resp_teacher["shape"]["width"]
    img_y = resp_teacher["shape"]["height"]
    for ques_teacher in resp_teacher["questions"]:
        ques_teacher_rec = (ques_teacher["location"][0]["y"]*img_y, ques_teacher["location"][0]["x"]*img_x,
                            ques_teacher["location"][1]["y"]*img_y, ques_teacher["location"][1]["x"]*img_x)
        # print(ques_teacher)
        for ques_stud in resp_student["questions"]:
            ques_stud_rec = (ques_stud["location"][0]["y"]*img_y, ques_stud["location"][0]["x"]*img_x,
                             ques_stud["location"][1]["y"]*img_y, ques_stud["location"][1]["x"]*img_x)
            q_iou = question_focus(ques_teacher_rec, ques_stud_rec)
            q_focus = {
                "questionID_t": int(),
                "questionID_s": int(),
                "answer_focus_list": []
            }
            print("question:" + str(q_iou))
            if q_iou > 0.2:  # 重合度大于0.7，说明题目是一致的
                # print(ques_teacher["questionID"])
                q_focus["questionID_t"] = ques_teacher["questionsID"]
                q_focus["questionID_s"] = ques_stud["questionsID"]

                for a_t in ques_teacher["answers"]:
                    a_t_rec = (a_t["location"][0]["y"] * img_y, a_t["location"][0]["x"] * img_x,
                               a_t["location"][1]["y"] * img_y, a_t["location"][1]["x"] * img_x)
                    for a_s in ques_stud["answers"]:
                        a_s_rec = (a_s["location"][0]["y"] * img_y, a_s["location"][0]["x"] * img_x,
                                   a_s["location"][1]["y"] * img_y, a_s["location"][1]["x"] * img_x)
                        a_iou = answer_focus(a_t_rec, a_s_rec)
                        print("answer:" + str(a_iou))
                        a_focus = {
                            "answerID_t": int(),
                            "answerID_s": int(),
                        }
                        if a_iou > 0.2:  # 重合度大于0.7，说明题目是一致的
                            a_focus["answerID_t"] = a_t["answersID"]
                            a_focus["answerID_s"] = a_s["answersID"]
                            q_focus["answer_focus_list"].append(a_focus)
                            focus_list.append(q_focus)
            # elif iou == 0: # 重合度等于0，说明题目是一致的
            #     break
    return focus_list
    # input()

        # ques_stud_rec =
        # question_focus()

def question_focus(rec1, rec2):
    iou = get_rect_iou(rec1, rec2)
    return iou

def answer_focus(rec1, rec2):
    iou = get_rect_iou(rec1, rec2)
    return iou

def to_correct(resp_teacher, resp_student):
    focus_list = get_focus(resp_teacher, resp_student)
    print(focus_list)
    # focus_list = [{'questionID_t': 0, 'questionID_s': 0, 'answer_focus_list': [{'answerID_t': 0, 'answerID_s': 0}]}]
    for focus in focus_list:
        for answer in focus["answer_focus_list"]:
            t_text = resp_teacher["questions"][focus["questionID_t"]]["answers"][answer["answerID_t"]]["text"]
            s_text = resp_student["questions"][focus["questionID_s"]]["answers"][answer["answerID_s"]]["text"]
            resp_student["questions"][focus["questionID_s"]]["answers"][answer["answerID_s"]]["corrector"] = correct(t_text, s_text)
    return resp_student

def correct(t_text, s_text):
    return 1

# 待定 假设shape都一样
# def reshape(resp_teach, resp_student):
#     """
#
#     :param resp_teach:
#     :param resp_student:
#     :return:
#     """
#     return new_resp_teach, new_resp_student

if __name__ == "__main__":
    pass
    # resp_teacher = {
    #     "imageID": 0,
    #     "shape": {
    #         "width": 800,
    #         "height": 1000
    #     },
    #     "questions": [
    #         {
    #             "questionsID": 0,
    #             "location": [  # 左上角，右上角
    #                 {
    #                     "x": 0.1,
    #                     "y": 0.1
    #                 },
    #                 {
    #                     "x": 0.2,
    #                     "y": 0.2
    #                 }
    #             ],
    #             "answers": [
    #                 {
    #                     "answersID": 0,
    #                     "location": [
    #                         {
    #                             "x": 0.12,
    #                             "y": 0.12
    #                         },
    #                         {
    #                             "x": 0.18,
    #                             "y": 0.18
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 }
    #             ]
    #         },
    #         {
    #             "questionsID": 1,
    #             "location": [  # 左上角，右上角
    #                 {
    #                     "x": 0.3,
    #                     "y": 0.3
    #                 },
    #                 {
    #                     "x": 0.4,
    #                     "y": 0.4
    #                 }
    #             ],
    #             "answers": [
    #                 {
    #                     "answersID": 0,
    #                     "location": [
    #                         {
    #                             "x": 0.32,
    #                             "y": 0.32
    #                         },
    #                         {
    #                             "x": 0.34,
    #                             "y": 0.34
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 },
    #                 {
    #                     "answersID": 1,
    #                     "location": [
    #                         {
    #                             "x": 0.35,
    #                             "y": 0.35
    #                         },
    #                         {
    #                             "x": 0.37,
    #                             "y": 0.37
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 }
    #             ]
    #         }
    #     ]
    # }
    # resp_student = {
    #     "imageID": 0,
    #     "shape": {
    #         "width": 800,
    #         "height": 1000
    #     },
    #     "questions": [
    #         {
    #             "questionsID": 0,
    #             "location": [  # 左上角，右上角
    #                 {
    #                     "x": 0.102,
    #                     "y": 0.103
    #                 },
    #                 {
    #                     "x": 0.21,
    #                     "y": 0.21
    #                 }
    #             ],
    #             "answers": [
    #                 {
    #                     "answersID": 0,
    #                     "location": [
    #                         {
    #                             "x": 0.12,
    #                             "y": 0.12
    #                         },
    #                         {
    #                             "x": 0.18,
    #                             "y": 0.18
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 }
    #             ]
    #         },
    #     ]
    # }
    # new_resp_student = to_correct(resp_teacher, resp_student)
    # print(resp_teacher, new_resp_student)
