# CHƯƠNG I. PHẢN ỨNG HÓA HỌC

---

# BÀI 6. TÍNH THEO PHƯƠNG TRÌNH HÓA HỌC

| Khái niệm, thuật ngữ | Kiến thức, kĩ năng |
|---|---|
| - Tính theo PTHH<br>- Lượng chất phản ứng, lượng sản phẩm<br>- Hiệu suất phản ứng ($H\%$) | - Tính được lượng chất (khối lượng, số mol hoặc thể tích chất khí) của chất phản ứng hoặc sản phẩm theo PTHH.<br>- Hiểu được ý nghĩa của hiệu suất phản ứng.<br>- Tính được hiệu suất phản ứng hoá học theo lượng chất thực tế và lượng chất lí thuyết. |

---

## 1. Các bước giải bài toán tính theo phương trình hoá học

Để giải bài toán tính khối lượng hoặc thể tích chất theo phương trình hoá học, ta thực hiện theo **4 bước chuẩn mực**:

```mermaid
graph LR
    A[Bước 1: Tính số mol chất đã cho n = m/M hoặc V/24.79] --> B[Bước 2: Viết & Cân bằng PTHH]
    B --> C[Bước 3: Dựa vào tỉ lệ PTHH để tìm số mol chất cần tính]
    C --> D[Bước 4: Chuyển đổi số mol sang m hoặc V theo yêu cầu đề bài]
```

### Ví dụ mẫu 1 (Tính thể tích khí theo khối lượng kim loại):
Đốt cháy hoàn toàn $4,8\text{ gam}$ kim loại magnesium ($\mathrm{Mg}$) trong khí oxygen thu được magnesium oxide ($\mathrm{MgO}$).
1. Viết phương trình hoá học của phản ứng.
2. Tính thể tích khí oxygen ($\mathrm{O}_2$) đã tham gia phản ứng ở điều kiện chuẩn ($25^\circ\mathrm{C}, 1\mathrm{ bar}$).
3. Tính khối lượng $\mathrm{MgO}$ sinh ra.

**Hướng dẫn giải chi tiết:**
- **Bước 1 (Tính số mol):**
  $$n_{\mathrm{Mg}} = \frac{m_{\mathrm{Mg}}}{M_{\mathrm{Mg}}} = \frac{4,8}{24} = 0,2\text{ (mol)}$$
- **Bước 2 (Viết PTHH):**
  $$2\mathrm{Mg} + \mathrm{O}_2 \xrightarrow{t^\circ} 2\mathrm{MgO}$$
- **Bước 3 (Tìm số mol chất cần tính theo tỉ lệ PTHH):**
  Theo phương trình: $2\text{ mol Mg}$ cần $1\text{ mol } \mathrm{O}_2$ và tạo ra $2\text{ mol MgO}$.
  $$\implies n_{\mathrm{O}_2} = \frac{1}{2} n_{\mathrm{Mg}} = \frac{1}{2} \cdot 0,2 = 0,1\text{ (mol)}$$
  $$\implies n_{\mathrm{MgO}} = n_{\mathrm{Mg}} = 0,2\text{ (mol)}$$
- **Bước 4 (Tính khối lượng và thể tích theo yêu cầu):**
  - Thể tích khí $\mathrm{O}_2$ ở đkc:
    $$V_{\mathrm{O}_2} = n \cdot 24,79 = 0,1 \cdot 24,79 = 2,479\text{ (lít)}$$
  - Khối lượng $\mathrm{MgO}$ sinh ra:
    $$m_{\mathrm{MgO}} = n \cdot M_{\mathrm{MgO}} = 0,2 \cdot (24 + 16) = 0,2 \cdot 40 = 8\text{ (gam)}$$

---

## 2. Hiệu suất của phản ứng hoá học ($H\%$)

Trong thực tế sản xuất hoặc thí nghiệm, do hóa chất bị hao hụt, phản ứng không xảy ra hoàn toàn hoặc có phản ứng phụ, nên lượng sản phẩm thu được trong thực tế luôn **nhỏ hơn** lượng tính toán theo lí thuyết.

> [!NOTE]
> **Khái niệm:**
> **Hiệu suất phản ứng** (kí hiệu $H\%$) là tỉ số phần trăm giữa lượng chất thu được trong thực tế và lượng chất tính theo lí thuyết (theo phương trình hoá học).

### Công thức tính hiệu suất phản ứng:
$$H\% = \frac{m_{\text{thực tế}}}{m_{\text{lí thuyết}}} \cdot 100\% \quad \text{hoặc} \quad H\% = \frac{n_{\text{thực tế}}}{n_{\text{lí thuyết}}} \cdot 100\%$$

$$\implies m_{\text{thực tế}} = \frac{m_{\text{lí thuyết}} \cdot H\%}{100\%}; \qquad m_{\text{lí thuyết}} = \frac{m_{\text{thực tế}} \cdot 100\%}{H\%}$$

*Ví dụ mẫu 2:*
Nung $50\text{ gam } \mathrm{CaCO}_3$, theo lí thuyết thu được $28\text{ gam } \mathrm{CaO}$. Nhưng khi thực hành trong lò nung chỉ thu được $22,4\text{ gam } \mathrm{CaO}$. Tính hiệu suất của phản ứng nung vôi:
$$H\% = \frac{22,4}{28} \cdot 100\% = 80\%$$

> [!TIP]
> **Mẹo ghi nhớ của Marie Curie:**
> Lượng thực tế bao giờ cũng $\le$ lượng lí thuyết (Hiệu suất $H\% \le 100\%$). Nếu em bấm máy tính ra $H\% > 100\%$ thì chắc chắn em đã đặt nhầm tử số và mẫu số rồi đấy nhé!
