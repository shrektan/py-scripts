# 给统计之都论坛的一道算法题回的帖子
# https://d.cosx.org/d/423739-yi-ge-si-kao-ti/15
library(data.table)
data = data.table(
  id = c(1:14),
  customer_id = c(rep(1, 2), rep(2, 3), rep(3, 5), rep(4, 4)),
  policy_id = c(123:124, rep(125, 3), 126:134),
  product = c(rep('A', 2), rep('B', 3), rep('C', 4), 'D', rep('E', 4)),
  fee = c(51, 51, 71, 31, 21, 28, 28, 28, 20, 51, 41, 31, 21, 11))

DT = data[, .(fee = sum(fee), ids = list(id)), keyby = .(customer_id, product, policy_id)]

cal = function(x, ids, out = NULL) {
  # x must be in accending order and all smaller than 50
  # x and ids must share the same length
  v_cumsum = cumsum(x)
  if (length(x) && v_cumsum[length(v_cumsum)] >= 50) {
    v_cumsum2 = v_cumsum + x[length(x)]
    i = which(v_cumsum2 >= 50)[1L]
    i = c(seq_len(i), length(x))
    out = list(unlist(ids[i]))
    ids = ids[-i]
    x = x[-i]
    if (sum(x) >= 50) {
      out = c(out, cal(x, ids))
    } else {
      out
    }
  }
}

no_of_letters = function(x, ids) {
  # x must be accending order
  # ids must be a list with the same length as x
  stopifnot(is.list(ids))
  out = ids[x >= 50]
  ids = ids[x < 50]
  x = x[x < 50]
  c(out, cal(x, ids))
}
# calculate the letter info
setorder(DT, fee)
out = DT[, .(letter_info = no_of_letters(fee, ids)), keyby = .(customer_id, product)]
out[, letter_id := seq_len(.N)]
print(out)

# merge back to the dataset
out2 = out[, .(id = unlist(letter_info)), keyby = .(customer_id, product, letter_id)]
data = out2[data, on = c("customer_id", "product", "id")]
print(data)

# check the result
data[!is.na(letter_id), .(fee = sum(fee)), keyby = .(customer_id, product, letter_id)] |> print()
