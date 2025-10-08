import database
import sqlite3
from pathlib import Path

from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.pickers import MDDockedDatePicker
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
    MDTextFieldHelperText,
    MDTextFieldTrailingIcon,
    MDTextFieldMaxLengthText,
)
from kivymd.uix.textfield.textfield import Validator

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.list import (
    MDListItem,
    MDListItemLeadingIcon,
    MDListItemSupportingText,
)

from kivy.lang import Builder
from kivy.core.window import Window

Window.size = (360, 720)

import sqlite3
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.fitimage import FitImage

def load_subscriptions(self):
    container = self.root.ids.subscriptions_container

    # Clear old cards
    container.clear_widgets()

    rows = database.load_suscriptions()
    print(rows)

    for id_suscripcion, id_plan, id_recordatorio, nombre, fecha_pago, monto_pago, medio_pago in rows:
        card = MDCard(
            style="elevated",
            size_hint_y=None,
            height=dp(80),
            radius=[20],
            padding=dp(12)
        )

        plan = database.load_plan_by_id(id_plan)

        layout = MDBoxLayout(orientation="horizontal", spacing=dp(12))
        card.add_widget(layout)

        # Image
        image = FitImage(source=f"product_imgs/{nombre}.png", size_hint=(None, None), size=(dp(56), dp(56)), radius=[12])
        layout.add_widget(image)

        # Info column
        info_col = MDBoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=None, width=dp(100))
        info_col.add_widget(MDLabel(text=nombre, halign="left", bold=True, text_color=(0,0,0,1)))
        info_col.add_widget(MDLabel(text=str(fecha_pago), halign="left", text_color=(0.4,0.4,0.4,1)))
        layout.add_widget(info_col)

        # Price column
        price_col = MDBoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=None, width=dp(100))
        price_col.add_widget(MDLabel(text=f"${monto_pago}", halign="right", bold=True, text_color=(0,0,0,1)))
        price_col.add_widget(MDLabel(text=plan[1], halign="right", text_color=(0.4,0.4,0.4,1)))
        layout.add_widget(price_col)

        container.add_widget(card)


class App(MDApp):
    dialog = None
    def build(self):
        return Builder.load_file("app.kv")
    
    def on_start(self):
        database.create_plan("Mensual", "30")
        database.check_db()
        load_subscriptions(self)

    def nueva_suscripcion(self):
        if not self.dialog:
            self.nombre_dialog = MDTextField(
                MDTextFieldLeadingIcon(
                    icon="credit-card-outline",
                ),
                MDTextFieldHintText(text="Servicio"),
                MDTextFieldMaxLengthText(max_text_length=16)
            )
            self.plan_dialog = MDTextField(
                MDTextFieldLeadingIcon(
                    icon="calendar-range",
                ),
                MDTextFieldHintText(text="Plan"),
                MDTextFieldMaxLengthText(max_text_length=16),
            )   
            
            self.fecha_pago_dialog = MDTextField(
                MDTextFieldLeadingIcon(
                    icon="pin",
                ),
                MDTextFieldHintText(text="Próximo pago"),
                MDTextFieldMaxLengthText(max_text_length=16),
                MDTextFieldHelperText(text="DD/MM/AAAA")
            )
            self.precio_dialog = MDTextField(
                MDTextFieldLeadingIcon(
                    icon="currency-usd",
                ),
                MDTextFieldHintText(text="Precio"),
                MDTextFieldMaxLengthText(max_text_length=16)
            )

            self.dialog = MDDialog(
                MDDialogIcon(icon="currency-usd"),
                MDDialogHeadlineText(text="Nueva Suscripción", halign="center"),
                MDDialogContentContainer(
                        self.nombre_dialog,
                        self.plan_dialog,
                        self.fecha_pago_dialog,
                        self.precio_dialog,
                        orientation="vertical",
                        spacing="32dp"
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Cancel"),
                        on_release=lambda *args: self.dialog.dismiss(),
                        style="text"
                    ),
                    MDButton(
                        MDButtonText(text="Add"),
                        on_release=self.guardar_servicio,
                        style="text"
                    ),
                    spacing="8dp",
                )
            )
        self.dialog.open()
        
    def guardar_servicio(self, *a):
        nombre = self.nombre_dialog.text.strip()
        plan = self.plan_dialog.text.strip()
        fecha_pago = self.fecha_pago_dialog.text.strip()
        precio = self.precio_dialog.text.strip()
        
        if not nombre or not plan or not fecha_pago or not precio:
            dialog = MDDialog(
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Aceptar")),
                        on_release=lambda *x: self.dialog.dismiss()
                ),
                MDDialogHeadlineText(text="Rellene todos los campos"),
            ).open()
            
            return
        
        print(f"User entered: {nombre}, {plan}, {fecha_pago}, {precio}")

        database.create_subscription(nombre, database.get_plan_id_from_string(plan), fecha_pago, precio, medio_pago="Extra")

        self.dialog.dismiss()
        load_subscriptions(self)

    def on_switch_tabs(
        self,
        bar: MDNavigationBar,
        item: MDNavigationItem,
        item_icon: str,
        item_text: str,
    ):
        self.root.ids.screen_manager.current = item_text

        button = self.root.ids.topbar_button
        button.opacity = 1 if item_text == "Suscripciones" else 0
        button.disabled = item_text != "Suscripciones"
    

App().run()
