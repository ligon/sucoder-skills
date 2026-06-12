;;; org-edit-review.el --- accept/reject the technical-editor's inline-task annotations -*- lexical-binding: t; -*-

;; Part of the technical-editor / research-writer adversarial prose loop.
;; The editor leaves Tier-2/3 critique as Org inline tasks (keywords EDIT /
;; REDLINE, closed by a "*************** END" line), kept out of export by the
;; file-level option `inline:nil'.  These commands let the author accept or
;; reject the task at point in the buffer.
;;
;; Contract for a REDLINE task (so accept can apply it automatically):
;;   *************** REDLINE :tier2:
;;   - old :: <exact text appearing in the preceding paragraph>
;;   - new :: <replacement text>
;;   - why :: <reason>
;;   *************** END
;; On accept, the FIRST exact occurrence of <old> searching BACKWARD from the
;; task is replaced by <new>, then the task is removed.  An EDIT (structural)
;; task carries no old/new; accept just removes it (the author makes the
;; structural change by hand) and reject records a rebuttal line.

(require 'org)
(require 'org-inlinetask)

(defun org-edit-review--task-bounds ()
  "Return (BEG . END) covering the inline task at point, or nil.
BEG is the start of the opening stars line; END is the end of the
closing `*************** END' line (including its newline)."
  (save-excursion
    (let* ((stars (make-string org-inlinetask-min-level ?*))
           (open-re (concat "^" (regexp-quote stars) "\\(?:\\*\\)? "))
           (end-re  (concat "^" (regexp-quote stars) "\\(?:\\*\\)? END[ \t]*$"))
           beg end)
      (end-of-line)
      (when (re-search-backward open-re nil t)
        (setq beg (line-beginning-position))
        (when (re-search-forward end-re nil t)
          (setq end (min (point-max) (1+ (line-end-position))))
          (cons beg end))))))

(defun org-edit-review--field (beg end label)
  "Return the value of a `- LABEL :: value' description line within BEG..END."
  (save-excursion
    (goto-char beg)
    (when (re-search-forward
           (concat "^[ \t]*-[ \t]*" (regexp-quote label) "[ \t]*::[ \t]*\\(.*\\)$")
           end t)
      (string-trim (match-string-no-properties 1)))))

(defun org-edit-review--keyword (beg)
  "Return the task keyword (\"EDIT\" or \"REDLINE\") at BEG."
  (save-excursion
    (goto-char beg)
    (when (looking-at (concat "^\\*\\{" (number-to-string org-inlinetask-min-level)
                              ",\\}\\(?:\\*\\)? +\\([A-Z]+\\)"))
      (match-string-no-properties 1))))

(defun org-edit-accept ()
  "Accept the editor inline task at point.
For a REDLINE, replace the preceding occurrence of its `old' text with
`new', then delete the task.  For an EDIT, just delete the task (the
author makes the structural change by hand)."
  (interactive)
  (let ((bounds (org-edit-review--task-bounds)))
    (unless bounds (user-error "Point is not on an editor inline task"))
    (let* ((beg (car bounds)) (end (cdr bounds))
           (kw  (org-edit-review--keyword beg)))
      (when (equal kw "REDLINE")
        (let ((old (org-edit-review--field beg end "old"))
              (new (org-edit-review--field beg end "new")))
          (unless (and old new)
            (user-error "REDLINE task missing `- old ::' or `- new ::'"))
          (save-excursion
            (goto-char beg)
            (if (search-backward old nil t)
                (replace-match new t t)
              (user-error "Could not find the `old' text before the task: %s" old)))))
      ;; delete the task region
      (delete-region beg end)
      (message "Accepted %s task." (or kw "editor")))))

(defun org-edit-reject (&optional reason)
  "Reject the editor inline task at point: leave prose, flip to RESOLVED,
and append a `- rebuttal :: REASON' line so the human sees the disagreement."
  (interactive)
  (let ((bounds (org-edit-review--task-bounds)))
    (unless bounds (user-error "Point is not on an editor inline task"))
    (let* ((beg (car bounds)) (end (cdr bounds))
           (reason (or reason (read-string "Rebuttal reason: "))))
      (save-excursion
        ;; flip keyword EDIT/REDLINE -> RESOLVED on the opening line
        (goto-char beg)
        (when (re-search-forward "\\(EDIT\\|REDLINE\\)" (line-end-position) t)
          (replace-match "RESOLVED" t t))
        ;; append rebuttal line just before the END line
        (goto-char beg)
        (let ((end-re (concat "^\\*\\{" (number-to-string org-inlinetask-min-level)
                              ",\\}\\(?:\\*\\)? END[ \t]*$")))
          (when (re-search-forward end-re nil t)
            (beginning-of-line)
            (insert (format "- rebuttal :: %s\n" reason)))))
      (message "Rejected; recorded rebuttal."))))

(provide 'org-edit-review)
;;; org-edit-review.el ends here
