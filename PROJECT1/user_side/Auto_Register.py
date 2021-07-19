import winreg as reg1
address1 = 'E:\\yud_bet\\PROJECT1\\user_side\\waiting_client.py'
key1 = reg1.HKEY_CURRENT_USER
key_value1 = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
open1 = reg1.OpenKey(key1, key_value1, 0, reg1.KEY_ALL_ACCESS)
reg1.SetValueEx(open1, "try1", 0, reg1.REG_SZ, address1)
