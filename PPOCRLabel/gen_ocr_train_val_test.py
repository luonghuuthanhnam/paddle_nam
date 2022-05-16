# coding:utf8
import os
import shutil
import random
import argparse


# Xóa tập hợp đào tạo đã chia, tập hợp xác thực và thư mục tập hợp kiểm tra và tạo lại một thư mục trống
def isCreateOrDeleteFolder(path, flag):
    flagPath = os.path.join(path, flag)

    if os.path.exists(flagPath):
        shutil.rmtree(flagPath)

    os.makedirs(flagPath)
    flagAbsPath = os.path.abspath(flagPath)
    return flagAbsPath


def splitTrainVal(root, absTrainRootPath, absValRootPath, absTestRootPath, trainTxt, valTxt, testTxt, flag):

# Chia tập huấn luyện, tập xác nhận và tập kiểm tra theo tỷ lệ đã chỉ định
    dataAbsPath = os.path.abspath(root)

    if flag == "det":
        labelFilePath = os.path.join(dataAbsPath, args.detLabelFileName)
    elif flag == "rec":
        labelFilePath = os.path.join(dataAbsPath, args.recLabelFileName)

    labelFileRead = open(labelFilePath, "r", encoding="UTF-8")
    labelFileContent = labelFileRead.readlines()
    random.shuffle(labelFileContent)
    labelRecordLen = len(labelFileContent)

    for index, labelRecordInfo in enumerate(labelFileContent):
        imageRelativePath = labelRecordInfo.split('\t')[0]
        imageLabel = labelRecordInfo.split('\t')[1]
        imageName = os.path.basename(imageRelativePath)

        if flag == "det":
            imagePath = os.path.join(dataAbsPath, imageName)
        elif flag == "rec":
            imagePath = os.path.join(dataAbsPath, "{}\\{}".format(args.recImageDirName, imageName))

# Chia tập huấn luyện, tập xác nhận và tập kiểm tra theo tỷ lệ đặt trước
        trainValTestRatio = args.trainValTestRatio.split(":")
        trainRatio = eval(trainValTestRatio[0]) / 10
        valRatio = trainRatio + eval(trainValTestRatio[1]) / 10
        curRatio = index / labelRecordLen

        if curRatio < trainRatio:
            imageCopyPath = os.path.join(absTrainRootPath, imageName)
            shutil.copy(imagePath, imageCopyPath)
            trainTxt.write("{}\t{}".format(imageCopyPath, imageLabel))
        elif curRatio >= trainRatio and curRatio < valRatio:
            imageCopyPath = os.path.join(absValRootPath, imageName)
            shutil.copy(imagePath, imageCopyPath)
            valTxt.write("{}\t{}".format(imageCopyPath, imageLabel))
        else:
            imageCopyPath = os.path.join(absTestRootPath, imageName)
            shutil.copy(imagePath, imageCopyPath)
            testTxt.write("{}\t{}".format(imageCopyPath, imageLabel))


# xóa các tệp hiện có
def removeFile(path):
    if os.path.exists(path):
        os.remove(path)


def genDetRecTrainVal(args):
    detAbsTrainRootPath = isCreateOrDeleteFolder(args.detRootPath, "train")
    detAbsValRootPath = isCreateOrDeleteFolder(args.detRootPath, "val")
    detAbsTestRootPath = isCreateOrDeleteFolder(args.detRootPath, "test")
    recAbsTrainRootPath = isCreateOrDeleteFolder(args.recRootPath, "train")
    recAbsValRootPath = isCreateOrDeleteFolder(args.recRootPath, "val")
    recAbsTestRootPath = isCreateOrDeleteFolder(args.recRootPath, "test")

    removeFile(os.path.join(args.detRootPath, "train.txt"))
    removeFile(os.path.join(args.detRootPath, "val.txt"))
    removeFile(os.path.join(args.detRootPath, "test.txt"))
    removeFile(os.path.join(args.recRootPath, "train.txt"))
    removeFile(os.path.join(args.recRootPath, "val.txt"))
    removeFile(os.path.join(args.recRootPath, "test.txt"))

    detTrainTxt = open(os.path.join(args.detRootPath, "train.txt"), "a", encoding="UTF-8")
    detValTxt = open(os.path.join(args.detRootPath, "val.txt"), "a", encoding="UTF-8")
    detTestTxt = open(os.path.join(args.detRootPath, "test.txt"), "a", encoding="UTF-8")
    recTrainTxt = open(os.path.join(args.recRootPath, "train.txt"), "a", encoding="UTF-8")
    recValTxt = open(os.path.join(args.recRootPath, "val.txt"), "a", encoding="UTF-8")
    recTestTxt = open(os.path.join(args.recRootPath, "test.txt"), "a", encoding="UTF-8")

    splitTrainVal(args.datasetRootPath, detAbsTrainRootPath, detAbsValRootPath, detAbsTestRootPath, detTrainTxt, detValTxt,
                  detTestTxt, "det")

    for root, dirs, files in os.walk(args.datasetRootPath):
        for dir in dirs:
            if dir == 'crop_img':
                splitTrainVal(root, recAbsTrainRootPath, recAbsValRootPath, recAbsTestRootPath, recTrainTxt, recValTxt,
                              recTestTxt, "rec")
            else:
                continue
        break



if __name__ == "__main__":
# Mô tả chức năng: tách biệt tập huấn luyện, tập xác nhận và tập kiểm tra để phát hiện và nhận dạng
# Mô tả: Bạn có thể điều chỉnh các thông số theo đường dẫn và nhu cầu của riêng mình Dữ liệu hình ảnh thường được nhiều người gắn nhãn theo lô Mỗi lô dữ liệu hình ảnh được đặt trong một thư mục và được gắn nhãn PPOCRLabel.
# Theo cách này, sẽ có nhiều thư mục hình ảnh được gắn nhãn để tổng hợp và phân chia tập huấn luyện, tập xác nhận và các yêu cầu của tập kiểm tra
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trainValTestRatio",
        type=str,
        default="6:2:2",
        help="ratio of trainset:valset:testset")
    parser.add_argument(
        "--datasetRootPath",
        type=str,
        default="../train_data/",
        help="path to the dataset marked by ppocrlabel, E.g, dataset folder named 1,2,3..."
    )
    parser.add_argument(
        "--detRootPath",
        type=str,
        default="../train_data/det",
        help="the path where the divided detection dataset is placed")
    parser.add_argument(
        "--recRootPath",
        type=str,
        default="../train_data/rec",
        help="the path where the divided recognition dataset is placed"
    )
    parser.add_argument(
        "--detLabelFileName",
        type=str,
        default="Label.txt",
        help="the name of the detection annotation file")
    parser.add_argument(
        "--recLabelFileName",
        type=str,
        default="rec_gt.txt",
        help="the name of the recognition annotation file"
    )
    parser.add_argument(
        "--recImageDirName",
        type=str,
        default="crop_img",
        help="the name of the folder where the cropped recognition dataset is located"
    )
    args = parser.parse_args()
    genDetRecTrainVal(args)
