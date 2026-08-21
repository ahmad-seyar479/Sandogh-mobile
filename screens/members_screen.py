# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder

import db
from utils.farsi_text import rtl

Builder.load_string("""
<MemberRow@BoxLayout>:
    size_hint_y: None
    height: "64dp"
    padding: ["10dp", "6dp"]
    spacing: "8dp"
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<MembersScreen>:
    BoxLayout:
        orientation: "vertical"

        TopBar:
            RTLButton:
                text: root.tr("بازگشت")
                size_hint_x: None
                width: "90dp"
                background_color: 0.4, 0.4, 0.42, 1
                on_release: root.manager.current = "dashboard"
            TitleLabel:
                text: root.tr("اعضا")
                color: 1, 1, 1, 1

        BoxLayout:
            size_hint_y: None
            height: "56dp"
            padding: "8dp"
            spacing: "8dp"
            RTLTextInput:
                id: search_box
                hint_text: root.tr("جستجو بر اساس نام یا شماره تماس")
                on_text: root.refresh(self.text)
            RTLButton:
                text: root.tr("+ عضو جدید")
                size_hint_x: None
                width: "130dp"
                on_release: root.add_member()

        ScrollView:
            GridLayout:
                id: member_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: "2dp"
""")


class MembersScreen(Screen):
    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        self.refresh(self.ids.search_box.text if "search_box" in self.ids else "")

    def refresh(self, query=""):
        container = self.ids.member_list
        container.clear_widgets()
        members = db.search_members(query)
        if not members:
            container.add_widget(Label(
                text=rtl("عضوی یافت نشد"), font_name="PersianFont",
                size_hint_y=None, height="60dp", color=(0.4, 0.4, 0.4, 1)))
            return
        for m in members:
            row = self._build_row(m)
            container.add_widget(row)

    def _build_row(self, member):
        row = BoxLayout(size_hint_y=None, height="64dp", padding=[10, 6], spacing=8)
        info = Label(
            text=rtl(f"{member['name']}   -   {member['phone'] or ''}"),
            font_name="PersianFont", halign="right", valign="middle",
            color=(0.15, 0.15, 0.15, 1))
        info.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        row.add_widget(info)
        from kivy.uix.button import Button
        open_btn = Button(text=rtl("مشاهده"), font_name="PersianFont",
                           size_hint_x=None, width="90dp",
                           background_normal="", background_color=(0.16, 0.45, 0.42, 1))
        open_btn.bind(on_release=lambda *_: self.open_member(member["id"]))
        row.add_widget(open_btn)
        return row

    def open_member(self, member_id):
        detail = self.manager.get_screen("member_detail")
        detail.member_id = member_id
        self.manager.current = "member_detail"

    def add_member(self):
        form = self.manager.get_screen("member_form")
        form.member_id = None
        self.manager.current = "member_form"
