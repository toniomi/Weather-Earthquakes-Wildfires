import customtkinter as ctk
import requests
import webbrowser
import folium
import os
from datetime import datetime, timedelta, timezone

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class MultiLangDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal Dashboard")
        self.geometry("720x880")
        self.resizable(False, False)

        # ----------------- APP STATE (DEFAULT: EN) -----------------
        self.current_lang = "EN"  
        self.current_lat = 37.9838
        self.current_lon = 23.7275
        self.city_name = ""
        self.active_earthquakes = [] 

        # ----------------- TRANSLATIONS DICTIONARY -----------------
        self.trans = {
            "GR": {
                "title": "🚨 Live Δεδομένα Τοποθεσίας & Κινδύνων",
                "weather_title": "🛰️ Εντοπισμός τοποθεσίας...",
                "temp_btn": "🌡️ Χάρτης Θερμ.",
                "eq_title": "🌋 Πρόσφατοι Σεισμοί (Όλα τα Ρίχτερ) - Τελευταίοι 10",
                "eq_btn": "🗺️ Χάρτης Σεισμών",
                "fire_title": "🔥 Ενεργές Εστίες / Πυρκαγιές (NASA) - 48h",
                "fire_btn": "🔥 Χάρτης Πυρκαγιών",
                "refresh_btn": "🔄 Ανανέωση Δεδομένων",
                "no_eq": "✅ Κανένας σεισμός δεν καταγράφηκε τις τελευταίες 48 ώρες.",
                "no_fire": "✅ Καμία ενεργή θερμική εστία δεν εντοπίστηκε τις τελευταίες 48 ώρες.",
                "eq_err": "❌ Σφάλμα κατά την ανάκτηση δεδομένων σεισμών.",
                "fire_err": "❌ Αδυναμία σύνδεσης με τη NASA.",
                "weather_err": "❌ Αποτυχία σύνδεσης με την υπηρεσία καιρού.",
                "spots_found": "⚠️ Εντοπίστηκαν {} πιθανές θερμικές εστίες:\n\n"
            },
            "EN": {
                "title": "🚨 Live Location & Hazard Data",
                "weather_title": "🛰️ Detecting location...",
                "temp_btn": "🌡️ Temp Map",
                "eq_title": "🌋 Recent Earthquakes (All Magnitudes) - Top 10",
                "eq_btn": "🗺️ EQ Map",
                "fire_title": "🔥 Active Thermal Spots / Fires (NASA) - 48h",
                "fire_btn": "🔥 Fire Map",
                "refresh_btn": "🔄 Refresh Data",
                "no_eq": "✅ No earthquakes detected in your region in the last 48 hours.",
                "no_fire": "✅ No active thermal hotspots detected in your region in the last 48 hours.",
                "eq_err": "❌ Error fetching earthquake data.",
                "fire_err": "❌ Error fetching NASA wildfire data.",
                "weather_err": "❌ Failed to connect to weather service.",
                "spots_found": "⚠️ Detected {} potential thermal hotspots nearby:\n\n"
            }
        }

        # ----------------- UI SETUP -----------------
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=20, pady=(10, 0))
        
    
        self.lang_btn = ctk.CTkButton(self.top_bar, text="🇬🇷 Switch to GR", width=100, fg_color="#34495e", hover_color="#2c3e50", command=self.toggle_language)
        self.lang_btn.pack(side="right")

        self.title_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=15)

        # Weather Section
        self.weather_frame = ctk.CTkFrame(self)
        self.weather_frame.pack(fill="x", padx=20, pady=10)
        
        self.weather_label = ctk.CTkLabel(self.weather_frame, text="", font=ctk.CTkFont(size=14), justify="left")
        self.weather_label.pack(pady=15, padx=15, side="left")

        self.radar_btn = ctk.CTkButton(self.weather_frame, text="", width=110, fg_color="#e67e22", hover_color="#d35400", command=self.open_temperature_map)
        self.radar_btn.pack(pady=15, padx=15, side="right")

        # Earthquakes Section
        self.eq_top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.eq_top_frame.pack(fill="x", padx=20, pady=(10, 0))

        self.eq_label_title = ctk.CTkLabel(self.eq_top_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.eq_label_title.pack(side="left", pady=5)

        self.eq_map_btn = ctk.CTkButton(self.eq_top_frame, text="", width=120, height=24, fg_color="#2ecc71", hover_color="#27ae60", command=self.open_earthquake_map)
        self.eq_map_btn.pack(side="right", pady=5)
        
        self.eq_textbox = ctk.CTkTextbox(self, width=680, height=180, font=ctk.CTkFont(size=12))
        self.eq_textbox.pack(padx=20, pady=5)
        self.eq_textbox.configure(state="disabled")

        # Wildfires Section
        self.fire_top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.fire_top_frame.pack(fill="x", padx=20, pady=(15, 0))

        self.fire_label_title = ctk.CTkLabel(self.fire_top_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.fire_label_title.pack(side="left", pady=5)

        self.fire_map_btn = ctk.CTkButton(
            self.fire_top_frame, 
            text="", 
            width=130, 
            height=24, 
            state="disabled", 
            fg_color="#7f8c8d", 
            command=self.open_fire_map
        )
        self.fire_map_btn.pack(side="right", pady=5)
        
        self.fire_textbox = ctk.CTkTextbox(self, width=680, height=180, font=ctk.CTkFont(size=12))
        self.fire_textbox.pack(padx=20, pady=5)
        self.fire_textbox.configure(state="disabled")

        self.refresh_btn = ctk.CTkButton(self, text="", command=self.load_all_data, fg_color="#1f538d", hover_color="#14375e")
        self.refresh_btn.pack(pady=20)

        self.update_ui_texts()
        self.load_all_data()

    def toggle_language(self):
        if self.current_lang == "EN":
            self.current_lang = "GR"
            self.lang_btn.configure(text="🇬🇧 Switch to EN")
        else:
            self.current_lang = "EN"
            self.lang_btn.configure(text="🇬🇷 Switch to GR")
        
        self.update_ui_texts()
        self.load_all_data()

    def update_ui_texts(self):
        lg = self.current_lang
        self.title_label.configure(text=self.trans[lg]["title"])
        self.radar_btn.configure(text=self.trans[lg]["temp_btn"])
        self.eq_label_title.configure(text=self.trans[lg]["eq_title"])
        self.eq_map_btn.configure(text=self.trans[lg]["eq_btn"])
        self.fire_label_title.configure(text=self.trans[lg]["fire_title"])
        self.fire_map_btn.configure(text=self.trans[lg]["fire_btn"])
        self.refresh_btn.configure(text=self.trans[lg]["refresh_btn"])

    def open_temperature_map(self):
        radar_url = f"https://www.windy.com/?temp,{self.current_lat},{self.current_lon},7"
        webbrowser.open(radar_url)

    def open_earthquake_map(self):
        if not self.active_earthquakes:
            return

        m = folium.Map(location=[self.current_lat, self.current_lon], zoom_start=6, control_scale=True)

        folium.Marker(
            location=[self.current_lat, self.current_lon],
            popup="Εσείς είστε εδώ / Your Location" if self.current_lang == "GR" else "Your Location",
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(m)

        for eq in self.active_earthquakes:
            folium.CircleMarker(
                location=[eq['lat'], eq['lon']],
                radius=max(int(eq['mag'] * 3), 5), 
                popup=f"<b>Magnitude:</b> {eq['mag']}<br><b>Place:</b> {eq['place']}<br><b>Time:</b> {eq['time']}",
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.4
            ).add_to(m)

        map_filename = "live_earthquake_map.html"
        m.save(map_filename)
        webbrowser.open('file://' + os.path.realpath(map_filename))

    def open_fire_map(self):
        fire_url = f"https://www.windy.com/?fires,{self.current_lat},{self.current_lon},7"
        webbrowser.open(fire_url)

    def update_textbox(self, textbox, text_content):
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text_content)
        textbox.configure(state="disabled")

    def load_all_data(self):
        lg = self.current_lang
        
        # 1. GEOLOCATION & WEATHER
        try:
            geo_res = requests.get("http://ip-api.com/json/").json()
            if geo_res.get("status") == "success":
                self.city_name = geo_res.get("city") if geo_res.get("city") else geo_res.get("country", "Unknown")
                self.current_lat = geo_res.get("lat", 37.9838)
                self.current_lon = geo_res.get("lon", 23.7275)
            else:
                self.city_name = "Greece" if lg == "GR" else "Default Location"

            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={self.current_lat}&longitude={self.current_lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&hourly=precipitation_probability&forecast_days=1"
            w_res = requests.get(w_url).json()
            c_data = w_res['current']
            rain_prob = w_res['hourly']['precipitation_probability'][0]
            
            if lg == "GR":
                weather_text = f"📍 Τοποθεσία: {self.city_name}\n🌡️ Θερμοκρασία: {c_data['temperature_2m']}°C  (Αίσθηση: {c_data['apparent_temperature']}°C)\n💧 Υγρασία: {c_data['relative_humidity_2m']}%  |  🌧️ Πιθανότητα Βροχής: {rain_prob}%\n💨 Άνεμος: {c_data['wind_speed_10m']} km/h"
            else:
                weather_text = f"📍 Location: {self.city_name}\n🌡️ Temperature: {c_data['temperature_2m']}°C  (Feels like: {c_data['apparent_temperature']}°C)\n💧 Humidity: {c_data['relative_humidity_2m']}%  |  Ref. Rain Probability: {rain_prob}%\n💨 Wind Speed: {c_data['wind_speed_10m']} km/h"
                
            self.weather_label.configure(text=weather_text)
        except Exception:
            self.weather_label.configure(text=self.trans[lg]["weather_err"])

        # 2. EARTHQUAKES
        try:
            now_utc = datetime.now(timezone.utc)
            time_48h_ago = (now_utc - timedelta(hours=48)).strftime('%Y-%m-%dT%H:%M:%S')
            
            if lg == "GR":
                eq_url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={time_48h_ago}&minlatitude=34.0&maxlatitude=42.0&minlongitude=19.0&maxlongitude=28.5&orderby=time&limit=10"
            else:
                eq_url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={time_48h_ago}&minlatitude={self.current_lat - 8.0}&maxlatitude={self.current_lat + 8.0}&minlongitude={self.current_lon - 8.0}&maxlongitude={self.current_lon + 8.0}&orderby=time&limit=10"
            
            eq_res = requests.get(eq_url).json()
            eq_output = ""
            self.active_earthquakes = [] 
            
            for event in eq_res['features']:
                p = event['properties']
                g = event['geometry']['coordinates'] 
                
                eq_time = datetime.fromtimestamp(p['time']/1000).strftime('%d/%m %H:%M')
                loc_label = "Περιοχή" if lg == "GR" else "Location"
                eq_output += f"• [{eq_time}]  Mag: {p['mag']}  |  {loc_label}: {p['place']}\n"
                
                self.active_earthquakes.append({
                    'lat': g[1],
                    'lon': g[0],
                    'mag': p['mag'],
                    'place': p['place'],
                    'time': eq_time
                })
            
            if not eq_output:
                eq_output = self.trans[lg]["no_eq"]
                self.eq_map_btn.configure(state="disabled", fg_color="#7f8c8d")
            else:
                self.eq_map_btn.configure(state="normal", fg_color="#2ecc71", hover_color="#27ae60")
                
            self.update_textbox(self.eq_textbox, eq_output)
        except Exception:
            self.update_textbox(self.eq_textbox, self.trans[lg]["eq_err"])
            self.eq_map_btn.configure(state="disabled", fg_color="#7f8c8d")

        # 3. WILDFIRES
        try:
            fire_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/964b4ec0f3933c06e88e8412ec09968a/VIIRS_SNPP_NRT/world/1"
            response = requests.get(fire_url)
            lines = response.text.split('\n')
            
            fire_output = ""
            count = 0
            for line in lines[1:]:
                data = line.split(',')
                if len(data) > 2:
                    f_lat = float(data[0])
                    f_lon = float(data[1])
                    
                    is_inside_bounds = False
                    if lg == "GR":
                        if 34.0 <= f_lat <= 42.0 and 19.0 <= f_lon <= 28.5:
                            is_inside_bounds = True
                    else:
                        if (self.current_lat - 4.0) <= f_lat <= (self.current_lat + 4.0) and (self.current_lon - 4.0) <= f_lon <= (self.current_lon + 4.0):
                            is_inside_bounds = True
                            
                    if is_inside_bounds:
                        acq_date = data[5]
                        acq_time = data[6]
                        label = "Εστία" if lg == "GR" else "Hotspot"
                        fire_output += f"• 🔥 {label} -> Lat: {f_lat}, Lon: {f_lon} | {acq_date} {acq_time} UTC\n"
                        count += 1
            
            if count == 0:
                fire_output = self.trans[lg]["no_fire"]
                self.fire_map_btn.configure(state="disabled", fg_color="#7f8c8d")
            else:
                fire_output = self.trans[lg]["spots_found"].format(count) + fire_output
                self.fire_map_btn.configure(state="normal", fg_color="#c0392b", hover_color="#962d22")
                
            self.update_textbox(self.fire_textbox, fire_output)
        except Exception:
            self.update_textbox(self.fire_textbox, self.trans[lg]["fire_err"])
            self.fire_map_btn.configure(state="disabled", fg_color="#7f8c8d")

if __name__ == "__main__":
    app = MultiLangDashboard()
    app.mainloop()