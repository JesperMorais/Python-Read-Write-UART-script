import serial
import threading
import time

PORT = 'COM3'   # Byt ut mot din port
BAUD = 115200   # Baudrate (samma som på ESP32)

lock = threading.Lock()
print_messages = True  # Kontroll om meddelanden ska visas
input_flag = False     # Flagga för skrivläge

# Funktion för att läsa inkommande data
def read_from_port(ser):
    global print_messages
    while True:
        try:
            data = ser.readline()  # Läs en rad
            if data and print_messages:  # Visa meddelanden om vi inte är i skrivläge
                with lock:
                    print(f"\rMottaget: {data.decode('utf-8', errors='ignore').strip()}")
                    print("Skriv 't' för att skicka ett meddelande > ", end='', flush=True)
        except Exception as e:
            print("Läsfel:", e)
            break

# Funktion för att lyssna på tangentbordet i bakgrunden
def keyboard_listener(ser):
    global print_messages, input_flag
    while True:
        user_input = input("\rSkriv 't' för att skicka ett meddelande > ").strip()
        if user_input.lower() == "t":
            print_messages = False  # Stoppa printning av inkommande meddelanden
            input_flag = True       # Sätt flagga för skrivläge
            with lock:
                message = input("Skriv ditt meddelande och tryck Enter: ")
                ser.write((message + "\n").encode('utf-8'))  # Skicka meddelandet
                print(f"Skickat: {message}")
            input_flag = False
            print_messages = True  # Återgå till att printa inkommande meddelanden

def main():
    try:
        # Öppna seriell port
        ser = serial.Serial(PORT, BAUD, timeout=0.1)
        print(f"Ansluten till {PORT} vid {BAUD} baud.")
        
        # Starta trådar för läsning och input
        read_thread = threading.Thread(target=read_from_port, args=(ser,), daemon=True)
        input_thread = threading.Thread(target=keyboard_listener, args=(ser,), daemon=True)
        read_thread.start()
        input_thread.start()
        
        # Håll programmet igång
        while True:
            time.sleep(0.1)
    
    except serial.SerialException as e:
        print(f"Fel: {e}")
    except KeyboardInterrupt:
        print("\nProgrammet avslutas...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Porten är stängd.")

if __name__ == "__main__":
    main()
