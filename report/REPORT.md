# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenAI, `openai:gpt-4.1-mini`, nhiệt độ 0, `recursion_limit=40`. Vòng thăm dò bằng `gpt-4o-mini` bị loại khỏi kết quả chính và lưu trong `results/gpt-4o-mini-archive/` vì model thường bỏ qua skill và hai lần bị recursion.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: Deep Agents 0.7.21; Windows, chạy trực tiếp trong `.venv`.
- Số lần chạy tác vụ đã dùng / ngân sách: 21 lượt task hoàn tất, hai lượt bị ngắt, hai smoke test và ba lần chạy curator. Chín kết quả chính hiện hành dùng 464.485 token; tính cả các lượt hoàn tất đã bị ghi đè, tổng task token quan sát được ít nhất 1.708.368, chưa gồm curator và lượt bị ngắt.
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): baseline sẽ đạt điểm eval cao hơn hoặc bằng subagents. Ở tập học, subagents không tăng điểm data/code, làm logs giảm từ 1/9 xuống 0/9, chỉ thực sự gọi một subagent mặc định nhưng vẫn tốn trung bình 57.327 so với 38.556 token (+49%). Đây cũng không phải bài toán có nhiều nhánh độc lập để tận dụng song song; kinh nghiệm triển khai của Anthropic cho thấy multi-agent phù hợp nhất với truy vấn breadth-first nhưng có chi phí token rất cao ([Anthropic, 2025](https://www.anthropic.com/engineering/multi-agent-research-system)).
- H2 (skills-auto so với baseline): skills-auto sẽ xấp xỉ baseline trên eval, không có cải thiện có hệ thống. Dù ba skill cuối mã hóa đúng nhiều lỗi tập học, cả ba lượt replay đều có `skills_read=0`, điểm vẫn 12/27 như baseline và token tăng 53%; vì vậy đường truyền tri thức chưa được kích hoạt. Dự đoán thận trọng này phù hợp với bằng chứng rộng hơn rằng skill được tuyển chọn có thể tăng pass rate ([SkillsBench, 2026](https://arxiv.org/abs/2602.12670)), nhưng skill tự sinh thường chỉ đem lại cải thiện cục bộ và không ổn định khi chuyển ngữ cảnh ([SkillEvolBench, 2026](https://skillevolbench.github.io/)).
- H3 (tác vụ học so với tác vụ đánh giá): điểm eval trung bình của cả ba điều kiện sẽ thấp hơn điểm học tương ứng, với mức giảm rõ nhất ở nhóm `rule_`. Tập học đã cho thấy 9/15 lỗi thuộc quy ước tổ chức và cả ba điều kiện đều đạt 0/9 check quy ước; skill lại được rút ra từ chính feedback học nên dễ đặc hiệu hóa cho quy ước cũ, trong khi frozen deployment kiểm tra khả năng chuyển giao sang bối cảnh/quy ước mới. SkillEvolBench cũng ghi nhận lợi ích khi học hoặc replay không nhất thiết tồn tại ở deployment đóng băng ([SkillEvolBench, 2026](https://skillevolbench.github.io/)).

## 3. Làm quen Deep Agents (Phần 0.3)

1.
2.
3.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | A. Bỏ qua đặc tả | `detail`: “the original files in tests/ must not be modified”. Đây là ràng buộc được nêu trực tiếp trong đề. |
| `data-learn` | `rule_money_in_cents` | E. Vi phạm quy ước tổ chức | `detail`: “RULE: money values in answer.json are integer cents”. |
| `data-learn` | `rule_meta_block` | E. Vi phạm quy ước tổ chức | `detail` yêu cầu đối tượng `meta` gồm `source`, `rows_in`, `rows_used`; đề bài không nêu quy ước này. |
| `data-learn` | `rule_clean_csv` | E. Vi phạm quy ước tổ chức | `detail` yêu cầu `clean.csv`, thứ tự cột, UTC, vùng chuẩn hóa và cents. |
| `code-learn` | `rule_type_hints` | E. Vi phạm quy ước tổ chức | `detail`: “RULE: every public function ... has type annotations ...”. |
| `code-learn` | `rule_regression_tests` | E. Vi phạm quy ước tổ chức | `detail`: “RULE: add tests/test_regressions.py ... at least 3”; tệp không được tạo. |
| `code-learn` | `rule_changelog` | E. Vi phạm quy ước tổ chức | `detail`: “RULE: record each fix in CHANGELOG.md under ... ## Unreleased”; tác tử không thực hiện. |
| `logs-learn` | `entry_count` | D. Bỏ sót dữ liệu bẩn hoặc định dạng | `detail`: “wrong number of entries (got 20)”; tác tử chưa tách đủ 25 entry lỗi. |
| `logs-learn` | `timestamps_utc` | D. Bỏ sót dữ liệu bẩn hoặc định dạng | `detail`: chỉ `17/25` timestamp đúng, cho thấy xử lý múi giờ hỗn hợp chưa đầy đủ. |
| `logs-learn` | `exception_fields` | D. Bỏ sót dữ liệu bẩn hoặc định dạng | `detail`: 8 giá trị `exception` sai; stack trace nhiều dòng chưa được ghép đúng. |
| `logs-learn` | `repeat_counts` | D. Bỏ sót dữ liệu bẩn hoặc định dạng | `detail`: 8 giá trị `repeat_count` sai; các dòng lặp sau entry chưa được xử lý đầy đủ. |
| `logs-learn` | `counts_by_service` | D. Bỏ sót dữ liệu bẩn hoặc định dạng | `detail`: `counts_by_service: wrong values`, là hệ quả của số entry và repeat count sai. |
| `logs-learn` | `rule_service_names` | E. Vi phạm quy ước tổ chức | `detail`: “RULE: service names ... lower-case with '-' replaced by '_'”. |
| `logs-learn` | `rule_sorted_errors` | E. Vi phạm quy ước tổ chức | `detail`: “RULE: errors is sorted by service, then by timestamp_utc”. |
| `logs-learn` | `rule_schema_header` | E. Vi phạm quy ước tổ chức | `detail`: yêu cầu `schema_version: 2` và `generated_by: log-triage`; đầu ra thiếu hai khóa này. |

Nhận xét: nhóm E chiếm đa số với 9/15 check thất bại; D có 5/15 và A có 1/15. `check_breakdown.py` xác nhận baseline đạt 12/18 check kỹ thuật nhưng 0/9 check quy ước. Cụ thể, toàn bộ 5 check kỹ thuật data và 6/7 check kỹ thuật code đã đạt; các lỗi kỹ thuật tập trung ở parser log. Vì vậy skill nên vừa mã hóa house rules cho từng họ tác vụ, vừa cung cấp checklist xử lý log nhiều dòng/múi giờ/dòng lặp.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế): `explorer` đọc đặc tả/dữ liệu và chỉ báo cáo; `implementer` sửa tệp rồi kiểm chứng; `reviewer` rà soát độc lập theo yêu cầu và trường hợp biên. Ba vai trò tách điều tra, thực thi và kiểm tra để giảm bỏ sót đặc tả.
- `subagent_calls` ở từng tác vụ và nhận xét: `data-learn=0`, `code-learn=0`, `logs-learn=1`. Lượt logs gọi subagent mặc định `general-purpose`, không gọi ba subagent tự định nghĩa.
- Thông tin thiếu hoặc thừa khi giao việc: prompt giao việc logs truyền đúng đường dẫn và hầu hết quy tắc công khai (level, UTC, message, traceback, repeat count, tổng theo service), nhưng chỉ nói chung “follow Acme conventions” nên không thể truyền các house rules chưa biết. Báo cáo subagent chứa kế hoạch và mã chưa được kiểm chứng; tác tử chính không chạy validator trước khi dùng, dẫn đến cấu trúc thiếu khóa và điểm 0/9.
- Ảnh hưởng đến token và thời gian: baseline trung bình 38.556 token và 20,7 giây; subagents 57.327 token và 31,7 giây, tăng khoảng 49% token. Điểm data và code giữ nguyên 5/8 và 6/10, còn logs giảm từ 1/9 xuống 0/9. Trong thí nghiệm học này, delegation không bù được chi phí.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: chạy curator 3 lần (lần đầu và tối đa 2 lần chạy lại theo GUIDE). Lần đầu xóa nguyên trạng `handle-file-not-found` vì học nhầm hậu quả của recursion. Lần hai tạo ba checklist đúng họ tác vụ nhưng vẫn dùng model cũ; toàn bộ được lưu trong archive. Lần ba dùng feedback baseline sạch của `gpt-4.1-mini` và sinh bộ ba skill cuối dưới đây. Không skill nào bị sửa tay.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `python-package-quality-checklist` | Tổng quát cho mọi tác vụ phát triển hoặc sửa gói Python; không chứa tên task, hàm hay đáp án riêng. | Đúng với feedback: type hints, không sửa test gốc, regression tests, changelog và chạy toàn bộ test. | 10 dòng. `description` kích hoạt rộng khi “develop or fix a Python package”; `skills_read=0` ở `code-learn`. |
| `structured-data-cleaning-and-validation-checklist` | Tổng quát cho CSV/dữ liệu bảng có chuẩn hóa, dedup, ngày giờ và đầu ra canonical. | Hầu hết đúng: xử lý định dạng ngày, vùng, missing/sentinel, duplicate, UTC, cents và metadata. Cụm “naive datetime” chỉ nên hiểu là biểu diễn nội bộ trước khi xuất UTC, nếu không có thể gây mơ hồ. | 16 dòng. `description` khớp trực tiếp `data-learn`; `skills_read=0`. |
| `log-file-error-triage-checklist` | Tổng quát cho log dịch vụ nhiều dòng; không chứa tên file đầu vào hay đáp án cụ thể. | Đúng và đầy đủ nhất: level không phân biệt hoa thường, UTC, service normalization, exception cuối stack trace, repeat count, sort và schema header. | 15 dòng. `description` khớp trực tiếp `logs-learn`; `skills_read=0`. |

Kết quả Phần 3.4: `data-learn=5/8`, `code-learn=6/10`, `logs-learn=1/9`; trung bình 58.944 token. `check_breakdown.py` cho `skills-auto` đạt 12/18 check kỹ thuật và 0/9 check quy ước, bằng baseline về điểm. Cả ba lượt có `skills_read=0`, trace không chứa lệnh đọc `skills/...`, dùng cùng `skills_sha256` và có `skills_modified=false`. Chẩn đoán offline bằng fake model xác nhận `FIRST action` và đủ ba tên/description skill thực sự nằm trong system prompt; do đó cơ chế thất bại là model không chọn đọc skill, không phải lỗi nạp của harness. Kết quả âm này được giữ nguyên, không chạy lặp để cherry-pick.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): vòng thăm dò `gpt-4o-mini` được lưu archive; đổi `LAB_MODEL=openai:gpt-4.1-mini`; smoke test; chạy từng task baseline và subagents với `--recursion-limit 40`; chạy curator lần cuối; đánh giá ba skill; chạy từng task `skills-auto`; `python scripts/check_breakdown.py`.
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác: không mở hoặc chạy bất kỳ tác vụ `*-eval` nào. Kết quả chính chỉ dùng `gpt-4.1-mini`; dữ liệu thăm dò model cũ nằm trong `results/gpt-4o-mini-archive/` và không dùng để kết luận chính.
