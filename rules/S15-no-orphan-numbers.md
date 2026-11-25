**S15. Mappability: no orphan numbers (CRITICAL).** Every number, table cell, and empirical claim
maps to a committed analysis script → a committed raw result file → (for reproduced prior-work
metrics) the source it reproduces. Maintain a provenance note (claim → value → script → raw
output). Numbers from the paper's
own data reach the text only through script-generated macros (the drafting rule "Numbers from data"); a data number
typed into the prose is a finding. New analysis code is committed to the correct repository, not a
scratch dir. If a number cannot be mapped, cut it or generate the mapping. Every technical claim
also carries a citation or a cross-reference to the section that cites it, and the cited source
says what the claim says, counts included. The exception is widely known facts in the community 
we're writing for do not need a citation. For example, "Linux is an open-source operating system 
kernel" is widely known and does not itself need a citation.
