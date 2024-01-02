# 绘制300etf的鳄鱼线

from src.internal.database.database import get_n_price_before_now, Frequency
from src.ui.display.draw import draw_alligator_line

if __name__ == '__main__':
    d1 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_H, 300)
    draw_alligator_line(d1)
