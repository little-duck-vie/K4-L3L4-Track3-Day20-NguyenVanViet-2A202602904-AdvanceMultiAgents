# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Văn Việt | 2A202602904 | Toàn bộ: harness, thí nghiệm, curator, đánh giá và báo cáo. |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenAI, `openai:gpt-4.1-mini`, nhiệt độ 0, `recursion_limit=40`. Vòng thăm dò bằng `gpt-4o-mini` bị loại khỏi kết quả chính và lưu trong `results/gpt-4o-mini-archive/` vì model thường bỏ qua skill và hai lần bị recursion.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: Deep Agents 0.7.21; Windows, chạy trực tiếp trong `.venv`.
- Số lần chạy tác vụ đã dùng / ngân sách: 36 lượt task hoàn tất, ba lượt bị ngắt hoặc lỗi, hai smoke test và ba lần chạy curator. Mười tám artifact kết quả chính hiện hành dùng 794.774 token; ba lượt mở rộng dùng thêm 178.836 token. Tính cả các lượt đã bị ghi đè, tổng task token quan sát được ít nhất 2.570.438, chưa gồm curator và lượt bị ngắt không ghi đủ usage.
- Commit của tag `freeze`: `cc618b2` (`freeze skills`); commit giả thuyết ngay trước đó là `435a066` (`hypotheses`).

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): baseline sẽ đạt điểm eval cao hơn hoặc bằng subagents. Ở tập học, subagents không tăng điểm data/code, làm logs giảm từ 1/9 xuống 0/9, chỉ thực sự gọi một subagent mặc định nhưng vẫn tốn trung bình 57.327 so với 38.556 token (+49%). Đây cũng không phải bài toán có nhiều nhánh độc lập để tận dụng song song; kinh nghiệm triển khai của Anthropic cho thấy multi-agent phù hợp nhất với truy vấn breadth-first nhưng có chi phí token rất cao ([Anthropic, 2025](https://www.anthropic.com/engineering/multi-agent-research-system)).
- H2 (skills-auto so với baseline): skills-auto sẽ xấp xỉ baseline trên eval, không có cải thiện có hệ thống. Dù ba skill cuối mã hóa đúng nhiều lỗi tập học, cả ba lượt replay đều có `skills_read=0`, điểm vẫn 12/27 như baseline và token tăng 53%; vì vậy đường truyền tri thức chưa được kích hoạt. Dự đoán thận trọng này phù hợp với bằng chứng rộng hơn rằng skill được tuyển chọn có thể tăng pass rate ([SkillsBench, 2026](https://arxiv.org/abs/2602.12670)), nhưng skill tự sinh thường chỉ đem lại cải thiện cục bộ và không ổn định khi chuyển ngữ cảnh ([SkillEvolBench, 2026](https://skillevolbench.github.io/)).
- H3 (tác vụ học so với tác vụ đánh giá): điểm eval trung bình của cả ba điều kiện sẽ thấp hơn điểm học tương ứng, với mức giảm rõ nhất ở nhóm `rule_`. Tập học đã cho thấy 9/15 lỗi thuộc quy ước tổ chức và cả ba điều kiện đều đạt 0/9 check quy ước; skill lại được rút ra từ chính feedback học nên dễ đặc hiệu hóa cho quy ước cũ, trong khi frozen deployment kiểm tra khả năng chuyển giao sang bối cảnh/quy ước mới. SkillEvolBench cũng ghi nhận lợi ích khi học hoặc replay không nhất thiết tồn tại ở deployment đóng băng ([SkillEvolBench, 2026](https://skillevolbench.github.io/)).

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định thấy chín tool: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute` và `task`. Tool `execute` chạy lệnh shell trong sandbox.
2. `task` mô tả `general-purpose` là subagent dùng cho nghiên cứu câu hỏi phức tạp, tìm file/nội dung và tác vụ nhiều bước; nó có cùng tập tool với tác tử chính. Mỗi lần gọi mặc định là stateless, chỉ thấy prompt được giao chứ không tự kế thừa hội thoại/ngữ cảnh của tác tử chính, rồi trả về một báo cáo cuối.
3. System prompt mặc định in ra là chuỗi rỗng. Hướng dẫn hành vi từ `task`: “Each invocation is stateless by default: the agent sees only the prompt you give it”. Hướng dẫn từ `execute`: “You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search.”

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

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 6/10 |
| data-learn | 5/8 | 5/8 | 5/8 |
| logs-learn | 1/9 | 0/9 | 1/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 3/9 | 1/9 | 3/9 |
| logs-eval | 1/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.45 | 0.41 | 0.45 |
| **Mean score - evaluation tasks** | 0.33 | 0.25 | 0.33 |
| **Mean tokens per run** | 38,339 | 45,077 | 49,046 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Breakdown do `scripts/check_breakdown.py` tái tạo:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     10/18         0/12          38,122      0/3
baseline      learn    12/18         0/9           38,556      0/3
subagents     eval      8/18         0/12          32,826      0/3
subagents     learn    11/18         0/9           57,327      0/3
skills-auto   eval     10/18         0/12          43,048      0/3
skills-auto   learn    12/18         0/9           55,043      0/3
```

Lượt đầu của `baseline/data-eval` chạm `GraphRecursionError` ở giới hạn 40 sau 176.112 token và được ghi 0/9. Theo GUIDE, tác vụ lỗi được chạy lại đúng một lần với cùng cấu hình; lượt hợp lệ 3/9, 25.793 token đã ghi đè artifact lỗi và được dùng trong bảng. Không lượt chính thức hiện hành nào có `error`; cả sáu lượt `skills-auto` đều có `skills_modified=false`, cùng hash đóng băng `c766b8663086a5af3a71edfeeeff6329bf7df564e7b3b283a9e43b82322cec0d`. `verify_freeze.py` báo `checked 6 runs of skill conditions: OK`.

## 8. Phân tích

1. Không điều kiện nào cải thiện tập học so với baseline: `skills-auto` hòa 0,45, còn `subagents` giảm xuống 0,41 do `logs-learn` từ 1/9 xuống 0/9. Trên eval, `skills-auto` cũng chỉ hòa baseline ở 0,33; `subagents` thấp hơn ở 0,25. Vì không có mẫu “tăng trên learn nhưng không tăng trên eval”, số điểm không trực tiếp chứng minh quá khớp; chúng cho thấy cả H1 (baseline không thua subagents) và H2 (skills-auto xấp xỉ baseline) được ủng hộ. H3 cũng đúng: từ learn sang eval, baseline và skills-auto giảm 0,12, subagents giảm 0,16.

2. `skills-auto` hòa baseline ở check kỹ thuật: 12/18 trên learn và 10/18 trên eval; cả hai đều đạt 0/9 và 0/12 check quy ước. Vì vậy curator chưa tạo cải thiện quan sát được cho nhóm nào. Ba quy ước mới chỉ có ở eval—`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`—đều thất bại; skill không chứa các quy tắc chưa từng xuất hiện này, và ngay cả quy tắc cũ được skill ghi lại cũng không được áp dụng vì agent không đọc skill.

3. Không có check nào có thể quy công cho skill một cách hợp lệ. Ví dụ `duplicate_events_removed` đạt ở `skills-auto/data-eval`, nhưng trace cho thấy agent tự đọc đề/dữ liệu rồi viết vòng lặp `seen_ids`; baseline cũng đạt check này và `skills_read=0`, nên đây là năng lực nền. Ngược lại, `rule_money_in_cents` thất bại dù `structured-data-cleaning-and-validation-checklist` có hướng dẫn chuyển tiền sang cents: trace không có lần đọc `skills/...`, output vẫn dùng số thực và thiếu các artifact quy ước. Cơ chế chính là lỗi kích hoạt/retrieval, chưa phải bằng chứng nội dung skill bị đọc rồi làm sai.

4. Trung bình trên sáu tác vụ, baseline dùng 38.339 token/lượt, subagents 45.077 (+17,6%) và skills-auto 49.046 (+27,9%). Nếu chuẩn hóa bằng số check đạt trên toàn bộ 230.036, 270.462 và 294.276 token, hiệu suất lần lượt là khoảng 0,096, 0,070 và 0,075 check đạt trên 1.000 token; baseline tốt nhất. Riêng tập học, subagents tốn hơn baseline 49% nhưng còn mất một check; trên eval nó dùng ít token hơn (32.826 so với 38.122 mỗi lượt) nhưng cũng chỉ đạt 8/30 thay vì 10/30. Với mức sử dụng subagent thấp và không tăng điểm, đa tác tử không đáng chi phí trong thí nghiệm này.

5. Không có dấu hiệu rò rỉ eval vào skill: H1–H3 ở commit `435a066`, skill được khóa tại tag `freeze` (`cc618b2`), không có eval nào được mở/chạy trước đó, diff skill sau tag rỗng và `verify_freeze.py` báo OK. Ba skill không chứa task id, tên file hay đáp án eval và sáu lượt dùng cùng hash. Tuy vậy có rủi ro quá khớp về nội dung: các checklist ghi chính xác quy ước học như cents, `meta`, changelog và schema header nhưng không thể biết ba quy ước mới của eval. Kết quả 0/12 house rule eval phù hợp với rủi ro chuyển giao này, song `skills_read=0` khiến thí nghiệm chưa tách được “skill quá khớp” khỏi “skill không được kích hoạt”.

6. Snapshot CP3 `results/skills-auto-dev/` và replay sau freeze dùng cùng hash, cùng đạt `code=6/10`, `data=5/8`, `logs=1/9`, tức chênh lệch điểm bằng 0 ở cả ba tác vụ và tổng vẫn 12/27. Token trung bình giảm từ 58.944 xuống 55.043, chênh 3.901 token (-6,6%), cho thấy đường chạy vẫn biến động dù điểm rời rạc không đổi. Không quan sát thấy nhiễu điểm trong ba cặp này không chứng minh hệ thống tất định; với một mẫu mỗi cấu hình, các chênh lệch nhỏ một check vẫn cần nhiều lần lặp mới có thể xem là ổn định.

## 9. Hạn chế và tính hợp lệ

1. Mỗi vai trò chỉ có ba tác vụ thuộc ba họ code, data và log. Mẫu nhỏ làm một check có thể thay đổi trung bình đáng kể và không cho phép suy rộng sang workflow khác.
2. Mỗi cặp điều kiện–tác vụ chỉ có một artifact hợp lệ. Nhiệt độ 0 không loại bỏ biến động do vòng lặp agent/tool; replay giữ điểm nhưng lệch 6,6% token, còn một lượt `baseline/data-eval` từng chạm recursion trước khi lần chạy lại hợp lệ đạt 3/9.
3. Thí nghiệm chính chỉ dùng `gpt-4.1-mini` với một phiên bản Deep Agents. Kết luận về retrieval, delegation và chi phí có thể đổi với model hoặc harness khác; archive `gpt-4o-mini` chỉ là thăm dò, không phải đối chứng chuẩn hóa.
4. House rules do benchmark cố ý giấu khỏi đề. Thiết kế này đo khả năng chuyển tri thức ngoài đề rất rõ, nhưng làm baseline không có con đường trực tiếp để suy ra 9 quy tắc learn và 12 quy tắc eval, nên không đại diện cho mọi dự án có tài liệu tổ chức đầy đủ.
5. Agent không đọc bất kỳ skill nào. Do đó kết quả đo toàn bộ pipeline gồm discovery/kích hoạt, nhưng không đo riêng chất lượng nội dung khi skill thực sự được sử dụng; không thể kết luận “skill vô ích” chỉ từ điểm hòa baseline.
6. Điều kiện subagents hiếm khi delegate và không dùng ba vai trò tùy chỉnh: 1/3 lượt learn và 2/3 lượt eval có gọi subagent, cả ba lần đều dùng `general-purpose`. Vì thế kết quả chủ yếu phản ánh quyết định không/ít giao việc của model, không phải trần năng lực của kiến trúc đa tác tử.

## 10. Kết luận

Trong sáu tác vụ, baseline đạt 22/57 check với chi phí thấp nhất; subagents đạt 19/57 và skills-auto đạt 22/57. Trên eval, skills-auto hòa baseline ở 0,33 và cả ba điều kiện đều đạt 0/12 house rules. Vì `skills_read=0` ở mọi lượt, kết quả không chứng minh nội dung skill không tốt mà chỉ chứng minh cơ chế hiện tại không chuyển được skill thành hành vi quan sát được. Đa tác tử cũng không đem lại lợi ích điểm đủ bù chi phí trong cấu hình này. Bước tiếp theo nên thêm router bắt buộc chọn và đọc skill liên quan trước hành động đầu tiên, rồi chạy đối chứng forced-read/không-skill qua nhiều seed để tách chất lượng skill khỏi lỗi kích hoạt.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): vòng thăm dò `gpt-4o-mini` được lưu archive; đổi `LAB_MODEL=openai:gpt-4.1-mini`; smoke test; chạy từng task học baseline và subagents với `--recursion-limit 40`; chạy curator lần cuối; đánh giá ba skill; chạy từng task học `skills-auto`; sao lưu `results/skills-auto-dev`; commit `hypotheses`; commit/tag `freeze`; chạy `baseline --tasks eval`, `subagents --tasks eval`, `skills-auto --tasks all`; chạy lại riêng `baseline/data-eval` bị recursion theo GUIDE; chạy `verify_freeze.py`, `lab.compare`, `check_breakdown.py` và `pytest`; chạy `python experiments/run_subagents_with_skills.py` và `python experiments/summarize_extension_6d.py`.
- Ghi chú khác: không mở hoặc chạy bất kỳ tác vụ `*-eval` nào trước commit/tag đóng băng. Kết quả chính chỉ dùng `gpt-4.1-mini`; dữ liệu thăm dò model cũ nằm trong `results/gpt-4o-mini-archive/` và không dùng để kết luận chính.

### Thử thách mở rộng 6d: subagent có skill

**Thiết kế.** Khi đồng thời bật subagents và skill, harness thêm `skills: ["/skills/"]` cùng chỉ dẫn đọc skill vào từng subagent tùy chỉnh; subagent mặc định của Deep Agents kế thừa skill middleware từ tác tử chính. Runner riêng đăng ký `subagents-skills` chỉ trong tiến trình thí nghiệm, dùng đúng skill đã đóng băng, model và `recursion_limit=40`, rồi ghi ba lượt eval vào `results/extension-6d/`. Vì `lab.compare` chỉ nhận ba điều kiện chính, kết quả mở rộng không thể làm đổi bảng ở mục 7.

| Task/metric | subagents | skills-auto | subagents-skills |
|---|---:|---:|---:|
| `code-eval` | 6/11 | 6/11 | 6/11 |
| `data-eval` | 1/9 | 3/9 | 1/9 |
| `logs-eval` | 1/10 | 1/10 | 1/10 |
| Điểm eval trung bình | 0,25 | 0,33 | 0,25 |
| Token trung bình/lượt | 32.826,3 | 43.048,7 | 59.612,0 |
| Tổng số lần gọi subagent | 2 | 0 | 0 |
| Lần đọc skill thấy trong main trace | 0 | 0 | 0 |

**Kết quả và cơ chế.** `subagents-skills` đạt 8/30 check, bằng subagents thường và thấp hơn skills-auto 10/30, nhưng tốn 178.836 token, tức 59.612 token/lượt—cao hơn subagents 81,6% và skills-auto 38,5%. Cả ba `run.json` đều có `subagent_calls=0`, `skills_read=0`, `skills_modified=false` và hash `c766b8663086a5af3a71edfeeeff6329bf7df564e7b3b283a9e43b82322cec0d`. Trace không có tool call `task` hay đường dẫn `skills/`: model tự xử lý như single agent, nên quyền đọc skill của subagent không bao giờ được sử dụng. Việc code vẫn đạt 6/11 đến từ sửa lỗi công khai và chạy ba test thành công; các house rules tiếp tục thất bại, phù hợp với cơ chế không kích hoạt chứ không chứng minh skill subagent sai.

**Hạn chế và bước tiếp theo.** Mỗi task chỉ chạy một lần; `skills_read` vốn chỉ đo main trace và không nhìn thấy thao tác bên trong subagent. Tuy nhiên trong ba lượt này `subagent_calls=0`, nên chắc chắn không có subagent nào được tạo để đọc skill. Thí nghiệm tiếp theo nên dùng router bắt buộc giao ít nhất một bước cho subagent phù hợp, bổ sung telemetry cho tool call nội bộ của subagent, rồi so sánh ba nhánh: subagent không skill, subagent có skill và forced-read qua nhiều seed.
