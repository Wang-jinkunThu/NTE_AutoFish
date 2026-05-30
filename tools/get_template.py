# 用法:
#   从已有截图选取模板:  python tools/get_template.py <image_path>
#   从游戏实时画面选取:  python tools/get_template.py --capture <模板名>
# 操作: 鼠标拖拽框选区域，Enter 确认，Esc 取消。输出到 assets/templates/

import cv2
import sys
import os


def select_roi(img):
    clone = img.copy()
    window = "Select ROI - drag to select, ENTER to confirm, ESC to quit"
    cv2.namedWindow(window)
    selecting = False
    start = (-1, -1)
    end = (-1, -1)

    def on_mouse(event, x, y, flags, param):
        nonlocal selecting, start, end
        if event == cv2.EVENT_LBUTTONDOWN:
            selecting = True
            start = (x, y)
            end = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and selecting:
            end = (x, y)
            display = clone.copy()
            cv2.rectangle(display, start, end, (0, 255, 0), 1)
            cv2.imshow(window, display)
        elif event == cv2.EVENT_LBUTTONUP:
            selecting = False
            end = (x, y)
            display = clone.copy()
            cv2.rectangle(display, start, end, (0, 255, 0), 1)
            cv2.imshow(window, display)

    cv2.setMouseCallback(window, on_mouse)
    cv2.imshow(window, clone)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter
            break
        elif key == 27:  # Esc
            print("Cancelled.")
            cv2.destroyAllWindows()
            sys.exit(0)

    x1, y1 = start
    x2, y2 = end
    x1, x2 = sorted([x1, x2])
    y1, y2 = sorted([y1, y2])

    if x2 - x1 < 1 or y2 - y1 < 1:
        print("Selection too small.")
        cv2.destroyAllWindows()
        sys.exit(1)

    cv2.destroyAllWindows()
    return x1, y1, x2, y2


def save_template(img, x1, y1, x2, y2, output_name):
    h, w = img.shape[:2]
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    alpha = rgba[:, :, 3].copy()
    alpha.fill(0)
    alpha[y1:y2, x1:x2] = 255
    rgba[:, :, 3] = alpha

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'templates')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{output_name}.png")
    cv2.imwrite(output_path, rgba)
    print(f"Saved: {output_path}")


def from_file(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to load image: {image_path}")
        sys.exit(1)

    x1, y1, x2, y2 = select_roi(img)
    base = os.path.splitext(os.path.basename(image_path))[0]
    save_template(img, x1, y1, x2, y2, base)


def from_capture(name):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from modules.controller import Controller

    c = Controller()
    try:
        img = c.screenshot()
        if img is None:
            print("screenshot() returned None")
            sys.exit(1)
    finally:
        c.camera.stop()

    x1, y1, x2, y2 = select_roi(img)
    save_template(img, x1, y1, x2, y2, name)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tools/get_template.py <image_path>        # from existing image")
        print("  python tools/get_template.py --capture <name>    # from live game capture")
        sys.exit(1)

    if sys.argv[1] == '--capture':
        name = sys.argv[2] if len(sys.argv) > 2 else "template"
        from_capture(name)
    else:
        from_file(sys.argv[1])
