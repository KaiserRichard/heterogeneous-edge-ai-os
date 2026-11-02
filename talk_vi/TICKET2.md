# TICKET TALK-VI-2: one script per speaker

Do not git commit. No GUI apps. Only change talk_vi/. Keep the existing speech text, numbers, page references and Q&A answers; this is a restructure.

Khánh's feedback: each person must get a script with ONLY their own lines. Khánh's file holds only Khánh's lines, same for Hiếu and Vinh.
Where another speaker takes over, put a short flow note in that person's file at that exact point, for example:
"(Trang 8–13 là phần của Vinh. Vinh mở đầu bằng: "…". Vinh kết bằng: "…". Nghe câu đó thì bạn nói tiếp.)"

Rebuild as three .docx, replacing the old ones:
- KichBan_Khanh.docx (delete KichBan_Khanh_BanTong.docx), KichBan_Hieu.docx, KichBan_Vinh.docx.
Each file, in speaking order:
1. Title with the speaker's name and total time, nothing about other speakers' content.
2. Their turns only, each beat: report page + mục, "Trang này nói gì", figure/table to point at, "Lời nói".
3. Between their turns, and before the first and after the last, the flow note (italic, shaded or boxed so it stands out): which pages the other person covers, the other person's real first and last sentence quoted from the script (short), and what to do next. Do not include the other speaker's full speech or Trang này nói gì.
4. The handoff sentence each person speaks stays in their own lines. Make sure each handoff sentence matches the next speaker's opening so it flows naturally; edit a handoff sentence only if needed.
5. Then only that person's Q&A, Từ cần nắm, Không nói. Khánh keeps moderator notes saying who answers which question, without the other people's answers.
Validate as before: zip, XML, pPr/rPr/tblPr order. Numbers must still all appear in talk_vi/report_source.docx.
