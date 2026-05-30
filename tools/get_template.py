import cv2
import sys
import os

def get_template(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to load image: {image_path}")
        sys.exit(1)

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

    h, w = img.shape[:2]
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    alpha = rgba[:, :, 3].copy()
    alpha.fill(0)
    alpha[y1:y2, x1:x2] = 255
    rgba[:, :, 3] = alpha

    base = os.path.splitext(os.path.basename(image_path))[0]
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'templates')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{base}.png")
    cv2.imwrite(output_path, rgba)
    print(f"Saved: {output_path}")

    cv2.destroyAllWindows()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python tools/get_template.py <image_path>")
        print("Drag to select the template area, then press ENTER to save or ESC to cancel.")
        sys.exit(1)
    get_template(sys.argv[1])
