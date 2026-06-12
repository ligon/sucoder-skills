;;; test-org-edit-review.el --- ERT tests for org-edit-review -*- lexical-binding: t; -*-

;; Regression tests for the technical-editor accept/reject/kill helper.
;; Run headless:
;;   emacs --batch -l org -l org-inlinetask \
;;     -l technical-editor/org-edit-review.el \
;;     -l technical-editor/test-org-edit-review.el \
;;     -f ert-run-tests-batch-and-exit
;;
;; The cases here pin the bugs found 2026-06: adjacent-task deletion (the END
;; line of one task matched as the opening of the next), accept buffer
;; corruption (prose replacement invalidated integer task positions), and
;; org-edit-kill point placement.

(require 'ert)
(require 'org)
(require 'org-inlinetask)
(require 'org-edit-review)

;; --- helpers ---------------------------------------------------------------

(defmacro org-edit-review-test--with (text &rest body)
  "Run BODY in a temp Org buffer initialised with TEXT.
Point starts at `point-min'; BODY positions it.  org-inlinetask is on."
  (declare (indent 1))
  `(with-temp-buffer
     (let ((org-inlinetask-min-level 15))
       (insert ,text)
       (org-mode)
       (goto-char (point-min))
       ,@body)))

(defun org-edit-review-test--goto (needle &optional line-offset)
  "Move point onto the line containing NEEDLE, plus optional LINE-OFFSET."
  (goto-char (point-min))
  (search-forward needle)
  (forward-line (or line-offset 0))
  (beginning-of-line))

(defconst org-edit-review-test--two-edits
  "#+OPTIONS: inline:nil
#+TODO: EDIT REDLINE | RESOLVED
* I
Prose one.
*************** EDIT first :structural:
obj one
*************** END
*************** EDIT second :structural:
obj two
*************** END
Prose two.
")

(defconst org-edit-review-test--edit-then-redline
  "#+OPTIONS: inline:nil
#+TODO: EDIT REDLINE | RESOLVED
* I
The field still lacks a disciplined framework here.
*************** EDIT note :structural:
buried punchline
*************** END
*************** REDLINE :tier2:
- old :: a disciplined framework
- new :: a framework
- why :: self-praising
*************** END
Tail sentence.
")

;; --- KILL ------------------------------------------------------------------

(ert-deftest org-edit-review/kill-single-from-body ()
  "Killing from the body removes exactly that task."
  (org-edit-review-test--with org-edit-review-test--two-edits
    (org-edit-review-test--goto "obj one")
    (org-edit-kill)
    (should-not (string-match-p "obj one" (buffer-string)))
    (should (string-match-p "obj two" (buffer-string)))
    ;; exactly one task remains: 2 star-lines (its opening + its END)
    (should (= 2 (length (org-edit-review-test--matches "^\\*\\{15\\}" (buffer-string)))))))

(ert-deftest org-edit-review/kill-from-END-line-does-not-eat-next ()
  "THE REPORTED BUG: killing with point on a task END line must not also
delete the following adjacent task."
  (org-edit-review-test--with org-edit-review-test--two-edits
    (org-edit-review-test--goto "obj one" 1)   ; the END line of the first task
    (should (string-match-p "END" (buffer-substring (line-beginning-position)
                                                    (line-end-position))))
    (org-edit-kill)
    (should-not (string-match-p "obj one" (buffer-string)))
    (should (string-match-p "obj two" (buffer-string)))
    (should (string-match-p "EDIT second" (buffer-string)))
    ;; exactly one task remains (2 star-lines: open + END)
    (should (= 2 (length (org-edit-review-test--matches "^\\*\\{15\\}" (buffer-string)))))))

(ert-deftest org-edit-review/kill-second-leaves-first ()
  (org-edit-review-test--with org-edit-review-test--two-edits
    (org-edit-review-test--goto "obj two")
    (org-edit-kill)
    (should (string-match-p "obj one" (buffer-string)))
    (should-not (string-match-p "obj two" (buffer-string)))))

(ert-deftest org-edit-review/kill-leaves-point-at-site ()
  "After kill, point sits at the prose seam where the task was."
  (org-edit-review-test--with
      "#+OPTIONS: inline:nil
* I
Alpha sentence.
*************** EDIT note :structural:
some objection
*************** END
Beta sentence.
"
    (org-edit-review-test--goto "some objection")
    (org-edit-kill)
    ;; the task is gone; point should be at the start of what followed it
    (should (looking-at-p "Beta sentence"))))

;; --- ACCEPT ----------------------------------------------------------------

(ert-deftest org-edit-review/accept-redline-applies-and-no-corruption ()
  "THE CORRUPTION BUG: accepting a REDLINE replaces old->new in the prose,
deletes only the redline task, leaves the adjacent EDIT intact, and does NOT
mangle the buffer (markers must survive the length-changing prose edit)."
  (org-edit-review-test--with org-edit-review-test--edit-then-redline
    (org-edit-review-test--goto "self-praising")
    (org-edit-accept)
    (let ((s (buffer-string)))
      (should (string-match-p "lacks a framework here" s))      ; new applied
      (should-not (string-match-p "disciplined framework" s))   ; old gone
      (should (string-match-p "buried punchline" s))            ; EDIT survives
      (should (string-match-p "Tail sentence\\." s))            ; tail intact
      ;; the REDLINE *task* is gone (the word still appears in the #+TODO
      ;; header keyword line, so check for the inline-task line, not the word)
      (should-not (string-match-p "^\\*\\{15\\}[^\n]*REDLINE" s))
      ;; exactly one task (the EDIT) remains: 2 star-lines
      (should (= 2 (length (org-edit-review-test--matches "^\\*\\{15\\}" s))))
      ;; no mangled star fragment left behind
      (should-not (string-match-p "\\*\\{1,14\\}[a-z]" s)))))

(ert-deftest org-edit-review/accept-edit-just-deletes ()
  "Accepting an EDIT (structural) deletes the task and leaves prose untouched."
  (org-edit-review-test--with org-edit-review-test--two-edits
    (org-edit-review-test--goto "obj one")
    (org-edit-accept)
    (should-not (string-match-p "obj one" (buffer-string)))
    (should (string-match-p "Prose one\\." (buffer-string)))    ; prose untouched
    (should (string-match-p "obj two" (buffer-string)))))       ; neighbour safe

(ert-deftest org-edit-review/accept-redline-missing-old-errors-cleanly ()
  "A REDLINE whose `old' text isn't in the prose errors without corrupting."
  (org-edit-review-test--with
      "#+OPTIONS: inline:nil
* S
Some prose without the target phrase.
*************** REDLINE
- old :: NONEXISTENT PHRASE
- new :: replacement
*************** END
"
    (org-edit-review-test--goto "REDLINE")
    (let ((before (buffer-string)))
      (should-error (org-edit-accept) :type 'user-error)
      ;; buffer unchanged after the failed accept
      (should (string= before (buffer-string))))))

;; --- REJECT ----------------------------------------------------------------

(ert-deftest org-edit-review/reject-flips-and-records ()
  "Reject leaves prose, flips keyword to RESOLVED, appends a rebuttal line,
and does not touch the adjacent task."
  (org-edit-review-test--with org-edit-review-test--two-edits
    (org-edit-review-test--goto "obj one" 1)   ; from the END line again
    (org-edit-reject "deliberate build-up")
    (let ((s (buffer-string)))
      (should (string-match-p "RESOLVED first" s))
      (should (string-match-p "- rebuttal :: deliberate build-up" s))
      (should (string-match-p "obj one" s))            ; prose/body kept
      (should (string-match-p "EDIT second" s)))))     ; neighbour untouched, still unresolved

;; --- guard -----------------------------------------------------------------

(ert-deftest org-edit-review/errors-when-not-on-task ()
  (org-edit-review-test--with org-edit-review-test--two-edits
    (org-edit-review-test--goto "Prose one")
    (should-error (org-edit-kill) :type 'user-error)
    (should-error (org-edit-accept) :type 'user-error)))

;; --- tiny regex helper used above -----------------------------------------

(defun org-edit-review-test--matches (re s)
  "Return a list of all matches of RE in string S (line-anchored ok)."
  (let ((start 0) acc)
    (while (string-match re s start)
      (push (match-string 0 s) acc)
      (setq start (1+ (match-beginning 0))))
    (nreverse acc)))

(provide 'test-org-edit-review)
;;; test-org-edit-review.el ends here
