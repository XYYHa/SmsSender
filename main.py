"""
短信发送器 - iOS毛玻璃风格UI + 后台Service
"""
import sys
import os
import time
import json
import threading
import random

# Kivy 核心
import kivy
kivy.require('2.0.0')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty,
    ColorProperty, ObjectProperty
)
from kivy.animation import Animation
from kivy.graphics import (
    Color, RoundedRectangle, Rectangle,
    Ellipse, PushMatrix, PopMatrix, Translate, Rotate,
    Canvas, Line, Fbo, ClearColor, ClearBuffers,
    Mesh
)
from kivy.graphics.texture import Texture
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp

# ========== iOS 玻璃效果工具 ==========

def hex_to_rgba(h, alpha=1.0):
    """十六进制转RGBA"""
    c = get_color_from_hex(h)
    return [c[0], c[1], c[2], alpha]

# iOS 调色板
IOS_COLORS = {
    'bg':        '#1C1C1E',   # 深色背景
    'card_bg':   '#2C2C2E',   # 卡片背景
    'label':     '#FFFFFF',   # 主文字
    'secondary': '#8E8E93',   # 次要文字
    'accent':    '#007AFF',   # iOS蓝
    'accent_disable': '#3A3A3C',
    'success':   '#34C759',   # iOS绿
    'danger':    '#FF3B30',   # iOS红
    'separator': '#38383A',
    'glass':     'rgba(44, 44, 46, 0.75)',  # 毛玻璃色
    'glass_light': 'rgba(255, 255, 255, 0.08)',
    'glass_border': 'rgba(255, 255, 255, 0.12)',
}

# ========== 毛玻璃卡片组件 ==========

class GlassCard(Widget):
    """iOS风格毛玻璃卡片"""
    radius = NumericProperty(dp(16))
    bg_color = ColorProperty(IOS_COLORS['card_bg'])
    border_alpha = NumericProperty(0.12)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, 
                  radius=self._draw, bg_color=self._draw,
                  border_alpha=self._draw)
        Clock.schedule_once(lambda dt: self._draw())
    
    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # 毛玻璃底层阴影
            Color(0, 0, 0, 0.3)
            RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[self.radius]
            )
            # 主卡片背景（半透明模拟玻璃）
            c = self.bg_color
            Color(c[0], c[1], c[2], c[3] * 0.85)
            RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[self.radius]
            )
            # 高光线（顶部边缘光）
            Color(1, 1, 1, 0.06)
            RoundedRectangle(
                pos=(self.x, self.y + self.height - dp(1)),
                size=(self.width, dp(1)),
                radius=[self.radius, self.radius, 0, 0]
            )
            # 边框
            Color(1, 1, 1, self.border_alpha)
            Line(
                rounded_rectangle=(
                    self.x, self.y, self.width, self.height, self.radius
                ),
                width=dp(0.5)
            )


class GlassButton(ButtonBehavior, Widget):
    """iOS风格毛玻璃按钮"""
    text = StringProperty('')
    sub_text = StringProperty('')
    accent = BooleanProperty(True)
    enabled = BooleanProperty(True)
    radius = NumericProperty(dp(14))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pressed = False
        self.bind(pos=self._draw, size=self._draw, text=self._draw,
                  accent=self._draw, enabled=self._draw, radius=self._draw)
        Clock.schedule_once(lambda dt: self._draw())
    
    def _draw(self, *args):
        self.canvas.before.clear()
        self.canvas.clear()
        
        w, h = self.width, self.height
        
        with self.canvas.before:
            if not self.enabled:
                Color(0.3, 0.3, 0.32, 0.5)
            elif self.accent:
                Color(*hex_to_rgba('#007AFF'))
            else:
                Color(1, 1, 1, 0.1)
            
            RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[self.radius]
            )
            
            # 按钮光泽
            if self.enabled:
                if self._pressed:
                    Color(0, 0, 0, 0.15)
                else:
                    Color(1, 1, 1, 0.08)
                RoundedRectangle(
                    pos=self.pos, size=self.size,
                    radius=[self.radius]
                )
        
        with self.canvas:
            # 文字
            from kivy.core.text import Label as CoreLabel
            
            # 主文本
            lbl = CoreLabel(
                text=self.text,
                font_size=sp(17),
                bold=True,
                color=[1,1,1,0.9 if self.enabled else 0.4],
                font_name='Roboto'
            )
            lbl.refresh()
            tex = lbl.texture
            tx = self.center_x - tex.width / 2
            ty = self.center_y - tex.height / 2 + dp(2) if self.sub_text else self.center_y - tex.height / 2
            Color(1, 1, 1, 1)
            Rectangle(texture=tex, pos=(tx, ty), size=tex.size)
            
            # 副文本
            if self.sub_text:
                lbl2 = CoreLabel(
                    text=self.sub_text,
                    font_size=sp(12),
                    color=[0.6, 0.6, 0.65, 0.7 if self.enabled else 0.3],
                )
                lbl2.refresh()
                tex2 = lbl2.texture
                tx2 = self.center_x - tex2.width / 2
                ty2 = ty - tex2.height - dp(2)
                Color(1, 1, 1, 1)
                Rectangle(texture=tex2, pos=(tx2, ty2), size=tex2.size)
    
    def on_touch_down(self, touch):
        if not self.enabled:
            return False
        if self.collide_point(*touch.pos):
            self._pressed = True
            self._draw()
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self._pressed:
            self._pressed = False
            self._draw()
        return super().on_touch_up(touch)


class StatusIndicator(Widget):
    """状态指示圆点"""
    active = BooleanProperty(False)
    color_active = ColorProperty(hex_to_rgba('#34C759'))
    color_inactive = ColorProperty(hex_to_rgba('#8E8E93'))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, active=self._draw,
                  color_active=self._draw, color_inactive=self._draw)
        Clock.schedule_once(lambda dt: self._draw())
    
    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            c = self.color_active if self.active else self.color_inactive
            Color(*c)
            Ellipse(
                pos=(self.center_x - dp(5), self.center_y - dp(5)),
                size=(dp(10), dp(10))
            )
            if self.active:
                # 呼吸光晕
                Color(*c[:3], 0.3)
                Ellipse(
                    pos=(self.center_x - dp(10), self.center_y - dp(10)),
                    size=(dp(20), dp(20))
                )


# ========== 主界面 ==========

class GlassDivider(Widget):
    """分隔线"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_once(lambda dt: self._draw())
    
    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 0.08)
            Rectangle(pos=(self.x, self.center_y), 
                     size=(self.width, dp(0.5)))


class SmsUI(FloatLayout):
    """主界面 - iOS毛玻璃风格"""
    
    # 状态
    is_running = BooleanProperty(False)
    phone = StringProperty('')
    duration = StringProperty('120')
    status_text = StringProperty('就绪')
    sent_count = NumericProperty(0)
    cycle_count = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = None
        self._core = None
        self._bg_texture = None
        self._count_timer = None
        
        # 生成背景渐变纹理
        Clock.schedule_once(self._generate_bg, 0)
        Clock.schedule_once(lambda dt: self._build_ui(), 0.05)
    
    def _generate_bg(self, dt):
        """生成动态毛玻璃背景 - 渐变色"""
        from kivy.graphics.texture import Texture
        
        w, h = 360, 780
        buf = bytearray()
        for y in range(h):
            ratio = y / h
            # 深色渐变: 顶部深紫蓝 -> 底部深绿
            r = int(28 + 20 * (1 - ratio))
            g = int(28 + 40 * ratio)
            b = int(46 + 10 * (1 - ratio))
            for x in range(w):
                # 加一点噪点纹理模拟玻璃
                noise = random.randint(-8, 8)
                buf.extend([
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise)),
                    255
                ])
        
        tex = Texture.create(size=(w, h), colorfmt='rgba')
        tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
        self._bg_texture = tex
        
        self._draw_bg()
    
    def _draw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self._bg_texture:
                Color(1, 1, 1, 1)
                Rectangle(texture=self._bg_texture, 
                         pos=self.pos, size=self.size)
            # 最上层雾化层
            Color(0, 0, 0, 0.2)
            Rectangle(pos=self.pos, size=self.size)
    
    def _build_ui(self):
        """构建UI元素"""
        self._draw_bg()
        
        # ===== 标题区 =====
        title_card = GlassCard(
            pos=(dp(20), self.height - dp(130)),
            size=(self.width - dp(40), dp(100)),
            radius=dp(20)
        )
        self.add_widget(title_card)
        
        # App 图标 + 标题
        from kivy.core.text import Label as CoreLabel
        
        # 标题文字（直接绘制在卡片上）
        self._title_label = CoreLabel(
            text='SMS Sender',
            font_size=sp(28),
            bold=True,
            color=[1,1,1,0.95]
        )
        self._title_label.refresh()
        self._title_tex = self._title_label.texture
        
        self._sub_label = CoreLabel(
            text='验证码发送工具',
            font_size=sp(14),
            color=[0.6, 0.6, 0.65, 0.7]
        )
        self._sub_label.refresh()
        self._sub_tex = self._sub_label.texture
        
        title_card.canvas.after.clear()
        with title_card.canvas.after:
            Color(1, 1, 1, 1)
            # 图标圆形
            Color(*hex_to_rgba('#007AFF'))
            Ellipse(pos=(title_card.x + dp(20), title_card.y + dp(20)),
                   size=(dp(60), dp(60)))
            # 图标中的"消息"图标简笔
            Color(1, 1, 1, 0.9)
            RoundedRectangle(
                pos=(title_card.x + dp(32), title_card.y + dp(35)),
                size=(dp(36), dp(30)),
                radius=[dp(6)]
            )
            Color(*hex_to_rgba('#007AFF'))
            RoundedRectangle(
                pos=(title_card.x + dp(36), title_card.y + dp(39)),
                size=(dp(28), dp(22)),
                radius=[dp(4)]
            )
            # 标题文字
            Color(1, 1, 1, 1)
            tex = self._title_tex
            Rectangle(texture=tex,
                     pos=(title_card.x + dp(95), 
                          title_card.y + dp(55) - tex.height/2),
                     size=tex.size)
            # 副标题
            tex2 = self._sub_tex
            Color(0.6, 0.6, 0.65, 0.7)
            Rectangle(texture=tex2,
                     pos=(title_card.x + dp(95),
                          title_card.y + dp(18)),
                     size=tex2.size)
        
        # ===== 输入区 =====
        input_card = GlassCard(
            pos=(dp(20), self.height - dp(300)),
            size=(self.width - dp(40), dp(150)),
            radius=dp(20)
        )
        self.add_widget(input_card)
        
        # 手机号输入
        self.phone_input = TextInput(
            text='',
            hint_text='输入手机号',
            hint_text_color=IOS_COLORS['secondary'],
            foreground_color=IOS_COLORS['label'],
            background_color=(1,1,1,0.05),
            cursor_color=IOS_COLORS['accent'],
            font_size=sp(20),
            size_hint=(None, None),
            size=(dp(280), dp(48)),
            pos=(input_card.x + dp(20), input_card.y + dp(85)),
            multiline=False,
            input_filter='int',
            padding=(dp(16), dp(12), dp(16), dp(12))
        )
        self.phone_input.bind(text=self._on_phone_change)
        self.add_widget(self.phone_input)
        
        # 手机号输入框的圆角
        with self.phone_input.canvas.before:
            Color(1, 1, 1, 0.06)
            RoundedRectangle(
                pos=self.phone_input.pos,
                size=self.phone_input.size,
                radius=[dp(12)]
            )
        
        # 时长输入
        self.duration_input = TextInput(
            text='120',
            hint_text='运行时长(秒)',
            hint_text_color=IOS_COLORS['secondary'],
            foreground_color=IOS_COLORS['label'],
            background_color=(1,1,1,0.05),
            cursor_color=IOS_COLORS['accent'],
            font_size=sp(16),
            size_hint=(None, None),
            size=(dp(130), dp(44)),
            pos=(input_card.x + dp(20), input_card.y + dp(25)),
            multiline=False,
            input_filter='int',
            padding=(dp(12), dp(10), dp(12), dp(10))
        )
        self.duration_input.bind(text=self._on_duration_change)
        self.add_widget(self.duration_input)
        
        with self.duration_input.canvas.before:
            Color(1, 1, 1, 0.06)
            RoundedRectangle(
                pos=self.duration_input.pos,
                size=self.duration_input.size,
                radius=[dp(12)]
            )
        
        # "秒" 标签
        sec_label = CoreLabel(
            text='秒',
            font_size=sp(15),
            color=[0.6, 0.6, 0.65, 0.7]
        )
        sec_label.refresh()
        sec_tex = sec_label.texture
        with self.duration_input.canvas.after:
            Color(0.6, 0.6, 0.65, 0.7)
            Rectangle(texture=sec_tex,
                     pos=(self.duration_input.right + dp(8),
                          self.duration_input.center_y - sec_tex.height/2),
                     size=sec_tex.size)
        
        # ===== 启动/停止按钮 =====
        self.action_btn = GlassButton(
            text='启动轰炸',
            sub_text='点击开始发送',
            accent=True,
            enabled=True,
            pos=(dp(20), self.height - dp(530)),
            size=(self.width - dp(40), dp(70)),
            radius=dp(18)
        )
        self.action_btn.bind(on_press=self._on_action)
        self.add_widget(self.action_btn)
        
        # ===== 状态卡片 =====
        status_card = GlassCard(
            pos=(dp(20), self.height - dp(660)),
            size=(self.width - dp(40), dp(110)),
            radius=dp(20)
        )
        self.add_widget(status_card)
        
        # 状态指示器（缓存文字纹理）
        status_labels = [
            ('状态', 0.7, status_card.y + dp(72)),
            ('已发送', 0.7, status_card.y + dp(40)),
            ('轮次', 0.7, status_card.y + dp(10)),
        ]
        
        status_card.canvas.after.clear()
        with status_card.canvas.after:
            for text, alpha, ypos in status_labels:
                lbl = CoreLabel(
                    text=text,
                    font_size=sp(12),
                    color=[0.6, 0.6, 0.65, alpha]
                )
                lbl.refresh()
                tex = lbl.texture
                Color(0.6, 0.6, 0.65, alpha)
                Rectangle(texture=tex,
                         pos=(status_card.x + dp(20), ypos),
                         size=tex.size)
        
        # 状态圆点
        self.status_dot = StatusIndicator(
            active=False,
            pos=(status_card.x + dp(90), status_card.y + dp(80)),
            size=(dp(30), dp(30))
        )
        self.add_widget(self.status_dot)
        
        # 状态文字
        self._status_text_label = CoreLabel(
            text='就绪',
            font_size=sp(16),
            color=[0.8, 0.8, 0.85, 0.9],
            bold=True
        )
        self._status_text_label.refresh()
        self._status_tex = self._status_text_label.texture
        
        with status_card.canvas.after:
            Color(0.8, 0.8, 0.85, 0.9)
            self._status_tex_ref = Rectangle(
                texture=self._status_tex,
                pos=(status_card.x + dp(115), 
                     status_card.y + dp(68)),
                size=self._status_tex.size
            )
        
        # 已发送计数
        self._count_label = CoreLabel(
            text='0',
            font_size=sp(20),
            color=[1,1,1,0.95],
            bold=True
        )
        self._count_label.refresh()
        self._count_tex = self._count_label.texture
        
        with status_card.canvas.after:
            Color(1, 1, 1, 0.95)
            self._count_tex_ref = Rectangle(
                texture=self._count_tex,
                pos=(status_card.x + dp(100), 
                     status_card.y + dp(30)),
                size=self._count_tex.size
            )
        
        # 轮次计数
        self._cycle_label = CoreLabel(
            text='0',
            font_size=sp(16),
            color=[0.8,0.8,0.85,0.85]
        )
        self._cycle_label.refresh()
        self._cycle_tex = self._cycle_label.texture
        
        with status_card.canvas.after:
            Color(0.8, 0.8, 0.85, 0.85)
            self._cycle_tex_ref = Rectangle(
                texture=self._cycle_tex,
                pos=(status_card.x + dp(85), 
                     status_card.y + dp(2)),
                size=self._cycle_tex.size
            )
        
        # ===== 底部信息 =====
        footer = CoreLabel(
            text='v1.0 · 后台运行中',
            font_size=sp(11),
            color=[0.5, 0.5, 0.55, 0.5]
        )
        footer.refresh()
        f_tex = footer.texture
        with self.canvas.after:
            Color(0.5, 0.5, 0.55, 0.5)
            Rectangle(texture=f_tex,
                     pos=(self.center_x - f_tex.width / 2, dp(20)),
                     size=f_tex.size)
    
    def _on_phone_change(self, instance, value):
        self.phone = value
    
    def _on_duration_change(self, instance, value):
        self.duration = value if value else '0'
    
    def _on_action(self, *args):
        if self.is_running:
            self._stop_service()
        else:
            self._start_service()
    
    def _start_service(self):
        phone = self.phone_input.text.strip()
        if not phone or len(phone) != 11 or not phone.isdigit():
            # 显示提示
            self._flash_message('请输入正确的11位手机号')
            return
        
        try:
            dur = int(self.duration_input.text)
            if dur < 10:
                dur = 120
        except:
            dur = 120
        
        self.is_running = True
        self.action_btn.text = '停止轰炸'
        self.action_btn.sub_text = '点击停止发送'
        self.action_btn.accent = False
        self.action_btn.enabled = True
        self.action_btn._draw()
        
        self.status_dot.active = True
        self._update_status_text('运行中...')
        
        # 启动后台服务
        self._start_backend(phone, dur)
    
    def _stop_service(self):
        self.is_running = False
        self.action_btn.text = '启动轰炸'
        self.action_btn.sub_text = '点击开始发送'
        self.action_btn.accent = True
        self.action_btn.enabled = True
        self.action_btn._draw()
        
        self.status_dot.active = False
        self._update_status_text('已停止')
        
        # 停止后台
        if self._core:
            self._core.exit_flag = True
    
    def _start_backend(self, phone, duration):
        """启动短信发送后台"""
        def run():
            try:
                core_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'sms_core.py'
                )
                # 如果资源在apk中
                if hasattr(sys, '_MEIPASS'):
                    core_path = os.path.join(sys._MEIPASS, 'sms_core.py')
                
                sys.path.insert(0, os.path.dirname(core_path))
                import importlib.util
                spec = importlib.util.spec_from_file_location("sms_core", core_path)
                core = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(core)
                self._core = core
                
                core.exit_flag = False
                core.print_lock = threading.Lock()
                
                # 缩短print输出到lambda更新UI
                original_print = core.print_lock.acquire
                
                # 启动
                p_thread = threading.Thread(
                    target=core.platform_sequential_worker,
                    args=(phone,), daemon=True
                )
                m_thread = threading.Thread(
                    target=core.minute_worker,
                    args=(phone,), daemon=True
                )
                p_thread.start()
                m_thread.start()
                
                # 定时更新计数
                count = 0
                end_time = time.time() + duration
                while time.time() < end_time and not core.exit_flag:
                    time.sleep(1)
                    count += 1
                    if count % 5 == 0:
                        Clock.schedule_once(
                            lambda dt: self._update_count(count)
                        )
                
                core.exit_flag = True
                Clock.schedule_once(lambda dt: self._on_backend_done())
                
            except Exception as e:
                print(f"Backend error: {e}")
                Clock.schedule_once(
                    lambda dt: self._flash_message(f'错误: {str(e)[:30]}')
                )
                Clock.schedule_once(lambda dt: self._stop_service())
        
        threading.Thread(target=run, daemon=True).start()
        
        # 动画更新计数
        self._count_timer = Clock.schedule_interval(
            lambda dt: self._update_count(
                int(time.time() * random.randint(1, 3))
            ) if self.is_running else None,
            2
        )
    
    def _on_backend_done(self):
        self._flash_message('任务完成')
        if self.is_running:
            self._stop_service()
    
    def _update_count(self, val):
        self.sent_count = val
        self._count_label = CoreLabel(
            text=str(val),
            font_size=sp(20),
            color=[1,1,1,0.95],
            bold=True
        )
        self._count_label.refresh()
        if hasattr(self, '_count_tex_ref'):
            self._count_tex_ref.texture = self._count_label.texture
            self._count_tex_ref.size = self._count_label.texture.size
    
    def _update_status_text(self, text):
        self._status_text_label = CoreLabel(
            text=text,
            font_size=sp(16),
            color=[0.8,0.8,0.85,0.9],
            bold=True
        )
        self._status_text_label.refresh()
        if hasattr(self, '_status_tex_ref'):
            self._status_tex_ref.texture = self._status_text_label.texture
            self._status_tex_ref.size = self._status_text_label.texture.size
    
    def _flash_message(self, msg):
        """底部闪现提示"""
        print(f"[UI] {msg}")


class SmsApp(App):
    """Kivy应用入口"""
    def build(self):
        # 窗口设置
        Window.size = (dp(390), dp(844))  # iPhone 14比例
        Window.minimum_width = dp(320)
        Window.minimum_height = dp(600)
        
        self.title = 'SMS Sender'
        self.icon = ''
        
        return SmsUI()


# ========== 启动入口 ==========
if __name__ == '__main__':
    # 判断是否在Android环境中
    is_android = False
    try:
        from android import AndroidService
        is_android = True
    except:
        pass
    
    if is_android:
        # Android: 先启动UI，Service后台逻辑由UI内的线程处理
        SmsApp().run()
    else:
        # 桌面端调试
        SmsApp().run()