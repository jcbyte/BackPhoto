import win32com.client


def get_mtp_devices():
  shell = win32com.client.Dispatch("Shell.Application")
  mtp_devices = shell.Namespace(17)  # 17 corresponds to "This PC" in Windows

  return mtp_devices.Items()