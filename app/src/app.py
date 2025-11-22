import database
import logging
logging.basicConfig(filename='session_metrics.log', level=logging.INFO)
import time
import datetime

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
        monto_int = int(round(monto_pago or 0))
        monto_clp = f"${monto_int:,}".replace(",", ".")

        price_col = MDBoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=None, width=dp(100))
        price_col.add_widget(MDLabel(text=monto_clp, halign="right", bold=True, text_color=(0,0,0,1)))
        price_col.add_widget(MDLabel(text=plan[1], halign="right", text_color=(0.4,0.4,0.4,1)))
        layout.add_widget(price_col)

        container.add_widget(card)

def load_expenses(self):
    self.root.ids.gasto_mensual_label.text = str(database.get_monthly_expense())

def load_next_subscription(self):
    row = database.get_next_subscription()

    img = self.root.ids.next_img
    name_label = self.root.ids.next_name
    date_label = self.root.ids.next_date
    price_label = self.root.ids.next_price
    plan_label = self.root.ids.next_plan

    if not row:
        img.source = "product_imgs/Spotify.png"
        name_label.text = "Sin suscripciones"
        date_label.text = ""
        price_label.text = ""
        plan_label.text = ""
        return

    id_suscripcion, id_plan, id_recordatorio, nombre, fecha_pago, monto_pago, medio_pago = row

    plan = database.load_plan_by_id(id_plan)

    monto_int = int(round(monto_pago or 0))
    monto_clp = f"${monto_int:,}".replace(",", ".")

    img.source = f"product_imgs/{nombre}.png"
    name_label.text = nombre
    date_label.text = fecha_pago
    price_label.text = monto_clp
    plan_label.text = plan[1]
    
class App(MDApp):
    dialog = None
    def build(self):
        return Builder.load_file("app.kv")
    
    def on_start(self):
        database.check_db()

        # Métricas
        self.start_time = time.time()
        logging.info("Aplicación iniciada")

        # Carga de datos
        load_expenses(self)
        load_next_subscription(self)
        load_subscriptions(self)

    def on_stop(self):
        elapsed = time.time() - self.start_time
        logging.info(f"Aplicación cerrada. Tiempo activo: {elapsed:.2f} segundos")

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
            save_dialog = MDDialog(
                MDDialogHeadlineText(text="Rellene todos los campos"),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Aceptar"),
                        on_release=lambda *x: save_dialog.dismiss()
                    ),
                ),
            )
            save_dialog.open()
            
            return
        

        database.create_subscription(nombre, database.get_plan_id_from_string(plan), fecha_pago, precio, medio_pago="Extra")

        self.dialog.dismiss()
        logging.info(f"Nueva suscripción guardada: {nombre} el {datetime.datetime.now()}")
        load_subscriptions(self)
        load_expenses(self)
        load_next_subscription(self)

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
