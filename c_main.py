#!/usr/local/anaconda3/envs/py39torch118/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2023/11/21 10:39
# @Author  : Berlin Wong
# @File    : c_main.py
# @Software: PyCharm

import sys
import os
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap, QPainterPath, QPen, QIcon


def resource_path(relative_path):
    """获取打包后的资源路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# 使用 resource_path 函数获取资源路径
# file_path = resource_path("relative_directory/file.txt")


class CircularWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle("Pomodoro Timer")

        # # 设置窗口属性为无边框
        # self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置窗口背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 去除窗口状态栏并将窗口置顶
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # 设置窗口的大小
        self.setGeometry(100, 100, 100, 100)

        # 用于记录鼠标拖动时的初始位置
        self.drag_start_position = None
        self.ctrl_pressed = False

        # 添加标签显示倒计时
        self.timer_label = QLabel(self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet(
            "font-size: 26px; color: #efefef;font-weight: bold; font-family:'汉仪尚巍手书W', Optima-Regular, Optima, PingFangSC-light, PingFangTC-light, 'PingFang SC', Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;")
        # self.timer_label.setGeometry(0, 100, self.width(), 100)
        self.timer_label.setGeometry(0, 0, 100, 100)

        # 初始化倒计时
        self.time_left = QTime(0, 25, 0)
        self.update_timer_label()

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        # 添加点击延迟处理相关变量
        self.delay_timer = QTimer(self)
        self.delay_timer.timeout.connect(self.reset_click_delay)
        self.click_delay = 10  # 设置延迟为10m秒
        self.is_running = False

    def paintEvent(self, event):

        # 在窗口绘制事件中绘制圆形
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)  # 设置抗锯齿渲染

        self.setWindowIcon(QIcon(resource_path("logo.png")))
        # painter.setRenderHint(QPainter.Antialiasing)

        # 创建圆形路径
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        painter.setClipPath(path)

        # 绘制背景图片
        pixmap = QPixmap(resource_path("logo.png"))  # 替换为你的图片路径
        painter.drawPixmap(0, 0, self.width(), self.height(), pixmap)

        # 绘制填充颜色的圆
        brush = QBrush(QColor(31, 31, 31, 128))
        painter.setBrush(brush)
        painter.drawEllipse(0, 0, self.width(), self.height())

        # 绘制白色边框的圆
        pen = QPen(Qt.white, 5)  # 设置边框颜色和宽度
        painter.setPen(pen)
        painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)

    def update_time(self):
        # 更新倒计时
        self.time_left = self.time_left.addSecs(-1)
        # print("Time left:" + str(self.time_left))
        self.update_timer_label()

        # 如果倒计时为零，停止定时器
        if self.time_left == QTime(0, 0, 0):
            self.timer.stop()

    def update_timer_label(self):
        # 更新标签显示
        self.timer_label.setText("" + self.time_left.toString("mm:ss"))

    def mousePressEvent(self, event):
        # 记录鼠标按下时的初始位置
        if event.button() == Qt.LeftButton:
            if self.drag_start_position is None:
                self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
                if True == self.ctrl_pressed:
                    if self.is_running:
                        return
                    self.is_running = True
                    self.timer.start(1000)
        if event.button() == Qt.RightButton:
            self.add_five_minutes()

    def add_five_minutes(self):
        # 检查是否在延迟时间内再次点击
        if self.delay_timer.isActive() or self.is_running:
            print("触发")
            return
        # 将倒计时增加五分钟，最大不超过30分钟
        new_time = self.time_left.addSecs(5 * 60)
        if new_time <= QTime(0, 30, 0):
            self.time_left = new_time
        else:
            self.time_left = QTime(0, 5, 0)
        # 更新倒计时标签
        self.update_timer_label()
        self.timer.stop()
        # 启动延迟定时器
        self.delay_timer.start(self.click_delay)

    def reset_click_delay(self):
        # 停止延迟定时器
        self.delay_timer.stop()

    def mouseMoveEvent(self, event):
        # 更新窗口位置，实现拖动
        if self.drag_start_position is not None:
            self.move(event.globalPos() - self.drag_start_position)

    def mouseReleaseEvent(self, event):
        # 清除拖动起始位置
        self.drag_start_position = None

    def mouseDoubleClickEvent(self, event):
        # 双击重置倒计时
        if event.button() == Qt.LeftButton:
            # print("Left button double-clicked")
            self.time_left = QTime(0, 25, 0)
            self.update_timer_label()
            self.timer.stop()
            self.is_running = False

    def keyPressEvent(self, event):
        # 按下Ctrl键时记录状态
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = True

    def keyReleaseEvent(self, event):
        # 释放Ctrl键时记录状态
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircularWindow()
    window.show()
    sys.exit(app.exec_())
