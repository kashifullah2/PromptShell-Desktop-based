try:
    from qfluentwidgets import FluentIcon as FIF
    print(f"MICROPHONE: {hasattr(FIF, 'MICROPHONE')}")
except ImportError:
    print("FluentIcon error")
