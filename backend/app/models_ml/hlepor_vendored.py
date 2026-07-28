"""Vendored from the `hlepor` package (0.0.4, unmaintained), with one change.

The original imports `NDArray` from `nptyping` purely for annotations. Line 1 of
the original is `from __future__ import annotations`, so those annotations were
never evaluated and nptyping did no work at runtime. But nptyping is unmaintained
and hard-caps numpy <2, which blocked numpy 2.x and Python 3.14 for the whole
backend.

So: the nptyping import is gone and its annotations now say `np.ndarray`, which
is what those values actually are. No behaviour change.
"""
from __future__ import annotations
import numpy as np
import collections
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from typing import List, Tuple, Callable, Counter, Any, Optional

def _separate_to_words(reference: List[str],
                       hypothesis: List[str],
                       preprocess: Callable[[str], str] = str.lower,
                       separate_punctuation: bool = True,
                       language: str = "english") -> Tuple[List[List[str]],
                                                           np.ndarray,
                                                           List[List[str]],
                                                           np.ndarray]:
    """
    Separate sentences of reference and hypothesis and return a tokenized copy of them, using NLTK's recommended
    word tokenizer. It assumes that reference and hypothesis have already been segmented into sentences.
    :param reference: reference sentences
    :param hypothesis: a hypothesis sentences
    :param preprocess: preprocessing method
    :param separate_punctuation: with the separation of punctuation from words(True value) or not(False)
    :param language: language of the reference and hypothesis
    :return: list of list of words and length of each line
    """
    reference_list, reference_length = _separate_sentences(reference, preprocess, separate_punctuation, language)
    hypothesis_list, hypothesis_length = _separate_sentences(hypothesis, preprocess, separate_punctuation, language)
    return reference_list, reference_length, hypothesis_list, hypothesis_length


def _separate_sentences(lines: List[str],
                        preprocess: Callable[[str], str] = str.lower,
                        separate_punctuation: bool = True,
                        language: str = "english") -> Tuple[List[List[str]], np.ndarray]:
    """
    Separate each sentence of the list into lists of words, using NLTK's recommended word tokenizer.
    :param lines: list of sentences
    :param preprocess: preprocessing method
    :param separate_punctuation: with the separation of punctuation from words(True value) or not(False)
    :param language: language of the reference and hypothesis
    :return: list of separated to words lines and length of each line
    """
    sep_lines = []
    length = []
    for line in lines:
        if line == '' or line != line:
            raise ValueError("Empty sentence. Exit.")
        try:
            if separate_punctuation:
                sep_words = word_tokenize(preprocess(line.strip()), language=language)
            else:
                sep_words = preprocess(line.strip()).split(' ')
        except AttributeError:
            print("\nWrong content of the list. It should be list of strings. Exit.")
            return [['']], np.array([np.nan])

        sep_lines.append(sep_words)
        length.append(len(sep_words))
    return sep_lines, np.array(length)


def enhanced_length_penalty(reference_length: np.ndarray,
                            hypothesis_length: np.ndarray) -> np.ndarray:
    """
    Return one of the components of the hLepor calculation - enhanced length penalty, which is defined to embrace
    the penalty for both longer and shorter hypothesis compared with the reference translations.
    :param reference_length: vector of reference sentences lengths
    :param hypothesis_length: vector of hypothesis sentences lengths
    :return: length penalty
    """
    numerator = np.maximum(reference_length, hypothesis_length)
    denominator = np.minimum(reference_length, hypothesis_length)
    return np.exp(1 - (numerator / denominator))


def _count_words(sentence: List[str]) -> Counter[str]:
    """
    Convert the list of words to dictionary with word as the key and how many times this word has occurred
    as corresponding value.
    :param sentence: list of words of one sentence
    :return: mapping between words and frequencies of their appearance in the sentence
    """
    return collections.Counter(sentence)


def _get_identical_words(ref_words_list: List[str],
                         hypo_words_list: List[str]) -> Counter[str, int]:
    """
    Make the mapping of matched words appearing both in reference and hypothesis, taking as the value the minimum count
    of the matches.
    :param ref_words_list: list of words of one reference sentence
    :param hypo_words_list: list of words of one hypothesis sentence
    :return: mapping between words and frequencies of their appearance in both reference and hypothesis
    """
    return _count_words(ref_words_list) & _count_words(hypo_words_list)


def _calc_aligned_num(matched_words_dict: Counter[str, int]) -> int:
    """
    Take the dictionary of matched words appearing both in reference and hypothesis sentence and calculate the
    summary number of aligned (matched) words.
    :param matched_words_dict: mapping between words and frequencies of their appearance in both reference and
    hypothesis
    :return: summary number of matched words in one sentence
    """
    return sum(matched_words_dict.values())


def _calc_precision(aligned_num: np.ndarray,
                    hypothesis_length: np.ndarray) -> np.ndarray:
    """
    Calculate precision: finds the quotient of dividing the summary number of matched words of each sentence by
    length of hypothesis sentences.
    :param aligned_num: the summary number of matched words of each sentence
    :param hypothesis_length: length of hypothesis sentences
    :return: vector of precision of each reference and hypothesis sentence pair
    """
    return aligned_num / hypothesis_length


def _calc_recall(aligned_num: np.ndarray,
                 reference_length: np.ndarray) -> np.ndarray:
    """
    Calculate recall: finds the quotient of dividing the summary number of matched words of each sentence by length
    of reference sentences.
    :param aligned_num: the summary number of matched words of each sentence
    :param reference_length: length of reference sentences
    :return: vector of recall of each reference and hypothesis sentence pair
    """
    return aligned_num / reference_length


def calc_harmonic_mean_p_r(aligned_num: np.ndarray,
                           reference_length: np.ndarray,
                           hypothesis_length: np.ndarray,
                           alpha: float = 9.0,
                           beta: float = 1.0) -> np.ndarray:
    """
    Take alpha and beta as the tunable weights for recall and precision respectively.
    Calculate precision, recall and weighted harmonic mean of precision and recall.
    :param aligned_num: the summary number of matched words of each sentence
    :param reference_length: length of reference sentences
    :param hypothesis_length: length of hypothesis sentences
    :param alpha: the tunable weight for recall
    :param beta: the tunable weight for precision
    :return: weighted Harmonic mean of precision and recall
    """
    p = _calc_precision(aligned_num, hypothesis_length)
    r = _calc_recall(aligned_num, reference_length)
    harmonic_mean_p_r = np.zeros((len(p)))
    nonzero_p_r = np.logical_or(p != 0, r != 0)
    nonzero_p = p[nonzero_p_r]
    nonzero_r = r[nonzero_p_r]
    harmonic_mean_p_r[nonzero_p_r] = (beta + alpha) / (beta / nonzero_p + alpha / nonzero_r)
    return harmonic_mean_p_r


def _label_positions(sentence_length: int) -> np.ndarray:
    """
    Construct the list of the position labels for each sentence. Position label is a vector of quotient values from
    1/m to m/m indicating the word position marked by sentence length which is m.
    :param sentence_length: length of the sentence
    :return: vector of position labels
    """
    return (np.arange(sentence_length) + 1) / sentence_length


def find_words_around(ref_words_list: List[str],
                      hypo_words_list: List[str],
                      ref_index: int,
                      hypo_index: int,
                      n: int = 2) -> bool:
    """
    Verify equal words around potentially matched word in reference and hypothesis. Return true if there is at least one
    equal word and false otherwise. n is the words count before and after matched word:
    if n = 2 then the function verifies two word before potentially matched word and two after.
    :param ref_words_list: list of words of one reference sentence
    :param hypo_words_list: list of words of one hypothesis sentence
    :param ref_index: index of the potentially matched word in reference
    :param hypo_index: index of the potentially matched word in hypothesis
    :param n: words count before and after matched word
    :return: true if there is at least one equal word and false otherwise
    """
    sub_ref = ref_words_list[ref_index - n: ref_index] + ref_words_list[ref_index + 1: ref_index + n + 1]
    sub_hypo = hypo_words_list[hypo_index - n: hypo_index] + hypo_words_list[hypo_index + 1: hypo_index + n + 1]

    for sh in sub_hypo:
        if sh in sub_ref:
            return True
    return False


def _find_position_difference(ref_words_list: List[str],
                              hypo_words_list: List[str],
                              ref_length: int,
                              hypo_length: int,
                              identical_words_dict: Counter[str, int],
                              n: int = 2) -> float:
    """
    Calculate position difference, i.e. n-gram position difference value between output and reference sentences.
    :param ref_words_list: list of words of one reference sentence
    :param hypo_words_list: list of words of one hypothesis sentence
    :param ref_length: length of the reference sentence
    :param hypo_length: length of the hypothesis sentence
    :param identical_words_dict: mapping between words and their frequencies both in reference and hypothesis
    :param n: words count before and after matched word
    :return: n-gram position difference value
    """
    ref_labels = _label_positions(ref_length)
    hypo_labels = _label_positions(hypo_length)
    pos_dif = 0
    for word in identical_words_dict:
        word_loc_ref = [index for index, elem in enumerate(ref_words_list) if elem == word]
        word_loc_hypo = [index for index, elem in enumerate(hypo_words_list) if elem == word]

        if len(word_loc_ref) == 1 == len(word_loc_hypo):  # if there is only one equal word
            pos_dif += np.abs(hypo_labels[word_loc_hypo[0]] - ref_labels[word_loc_ref[0]])
            continue
        for word_index in word_loc_hypo:
            if len(word_loc_ref) > 0:
                words_count = []
                for ref_index in word_loc_ref:
                    words_count.append(find_words_around(ref_words_list, hypo_words_list, ref_index, word_index, n))

                ref_ind_equal_word = np.array(word_loc_ref)[words_count]
                if len(ref_ind_equal_word) > 0:
                    nearest_index = np.argmin(
                        np.abs(np.array([word_index] * len(ref_ind_equal_word)) - np.array(ref_ind_equal_word)))
                else:
                    nearest_index = np.argmin(
                        np.abs(np.array([word_index] * len(word_loc_ref)) - np.array(word_loc_ref)))

                ref_matched_index = word_loc_ref[nearest_index]
                word_loc_ref.pop(nearest_index)

                pos_dif += np.abs(hypo_labels[word_index] - ref_labels[ref_matched_index])
    return pos_dif


def _calc_hlepor(elp: np.ndarray,
                 n_pos_penal: np.ndarray,
                 hpr: np.ndarray,
                 weight_elp: float = 2.0,
                 weight_pos: float = 1.0,
                 weight_pr: float = 7.0) -> np.ndarray:
    """
    Calculate hLepor metric by enhanced length penalty, n-gram position difference penalty and harmonic mean
    of precision and recall with tunable weights.
    :param elp: enhanced length penalty for each reference and hypothesis sentence pair
    :param n_pos_penal: n-gram position difference penalty for each reference and hypothesis sentence pair
    :param hpr: harmonic mean of precision and recall for each reference and hypothesis sentence pair
    :param weight_elp: tunable weight of enhanced length penalty
    :param weight_pos: tunable weight of n-gram position difference penalty
    :param weight_pr: tunable weight of harmonic mean of precision and recall
    :return: hLepor value for each hypothesis sentence
    """
    hlepor_sentence = np.zeros((len(elp)))
    nonzero_mask = np.logical_and(np.logical_and(elp > 0, n_pos_penal > 0), hpr > 0)
    elp_nonzero = elp[nonzero_mask]
    n_pos_penal_nonzero = n_pos_penal[nonzero_mask]
    hpr_nonzero = hpr[nonzero_mask]
    hlepor_sentence[nonzero_mask] = (weight_elp + weight_pos + weight_pr) / (weight_elp
                                                                                   / elp_nonzero + weight_pos
                                                                                   / n_pos_penal_nonzero + weight_pr / hpr_nonzero)
    return hlepor_sentence


def hlepor_score(reference: List[str],
                 hypothesis: List[str],
                 alpha: float = 9.0,
                 beta: float = 1.0,
                 n: int = 2,
                 weight_elp: float = 2.0,
                 weight_pos: float = 1.0,
                 weight_pr: float = 7.0,
                 preprocess: Callable[[str], str] = str.lower,
                 separate_punctuation: bool = True,
                 language: str = "english") -> Optional[float]:
    """
    Calculate hLepor score (Harmonic mean of enhanced Length Penalty, Precision, n-gram Position difference Penalty and
    Recall) Aaron Li-Feng Han, Derek F. Wong, Lidia S. Chao, Liangye He Yi Lu, Junwen Xing, and Xiaodong Zeng. 2013.
    "Language-independent Model for Machine Translation Evaluation with Reinforced Factors".
    In Proceedings of the XIV Machine Translation Summit.
    https://www.researchgate.net/profile/Aaron-L-F-Han/publication/256460090_MT_SUMMIT13Language-independent_Model_for_Machine_Translation_Evaluation_with_Reinforced_Factors/links/00463522d48942210c000000/MT-SUMMIT13Language-independent-Model-for-Machine-Translation-Evaluation-with-Reinforced-Factors.pdf
    >>> reference = ['It is a guide to action that ensures that the military will forever heed Party commands',
                     'It is the practical guide for the army always to heed the directions of the party']
    >>> hypothesis = ['It is a guide to action which ensures that the military always obeys the commands of the party',
                      'It is to insure the troops forever hearing the activity guidebook that party direct']
    >>> round(hlepor_score(reference, hypothesis), 4)
    0.6214
    :param reference: reference sentences
    :param hypothesis: hypothesis sentences
    :param alpha: the tunable weight for recall
    :param beta: the tunable weight for precision
    :param n: words count before and after matched word in npd calculation
    :param weight_elp: tunable weight of enhanced length penalty
    :param weight_pos: tunable weight of n-gram position difference penalty
    :param weight_pr: tunable weight of harmonic mean of precision and recall
    :param weight_pr: tunable weight of harmonic mean of precision and recall
    :param preprocess: preprocessing method
    :param separate_punctuation: with the separation of punctuation from words(True value) or not(False)
    :param language: language of the reference and hypothesis
    :return: mean hLepor metric value of input strings
    """
    if len(reference) != len(hypothesis):
        raise ValueError("Reference and hypothesis lengths must be the same. Exit.")
    if len(reference) == 0 or len(hypothesis) == 0:
        print("There is an empty list. Exit.")
        return
    reference_list, reference_length, hypothesis_list, hypothesis_length = _separate_to_words(reference, hypothesis,
                                                                                              preprocess,
                                                                                              separate_punctuation,
                                                                                              language)
    if np.isnan(reference_length[0]) or np.isnan(hypothesis_length[0]):
        return
    sentence_count = len(reference_length)
    elp = enhanced_length_penalty(reference_length, hypothesis_length)
    aligned_num = np.zeros(sentence_count)
    npd = np.zeros(sentence_count)
    for i in range(sentence_count):
        if hypothesis_list[i] == reference_list[i]:
            npd[i] = 0
            aligned_num[i] = reference_length[i]
            continue
        identical_words_dict = _get_identical_words(reference_list[i], hypothesis_list[i])
        aligned_num[i] = _calc_aligned_num(identical_words_dict)
        pos_dif = _find_position_difference(reference_list[i], hypothesis_list[i], reference_length[i],
                                            hypothesis_length[i], identical_words_dict, n)
        npd[i] = pos_dif / hypothesis_length[i]
    n_pos_penal = np.exp(-npd)
    hpr = calc_harmonic_mean_p_r(aligned_num, reference_length, hypothesis_length, alpha, beta)
    hlepor = _calc_hlepor(elp, n_pos_penal, hpr, weight_elp, weight_pos, weight_pr)
    return np.mean(hlepor)


def single_hlepor_score(reference: str,
                        hypothesis: str,
                        alpha: float = 9.0,
                        beta: float = 1.0,
                        n: int = 2,
                        weight_elp: float = 2.0,
                        weight_pos: float = 1.0,
                        weight_pr: float = 7.0,
                        preprocess: Callable[[str], str] = str.lower,
                        separate_punctuation: bool = True,
                        language: str = "english") -> Optional[float]:
    """
    Calculate hLepor score of single sentence pair (Harmonic mean of enhanced Length Penalty, Precision, n-gram Position difference Penalty and
    Recall) Aaron Li-Feng Han, Derek F. Wong, Lidia S. Chao, Liangye He Yi Lu, Junwen Xing, and Xiaodong Zeng. 2013.
    "Language-independent Model for Machine Translation Evaluation with Reinforced Factors".
    In Proceedings of the XIV Machine Translation Summit.
    https://www.researchgate.net/profile/Aaron-L-F-Han/publication/256460090_MT_SUMMIT13Language-independent_Model_for_Machine_Translation_Evaluation_with_Reinforced_Factors/links/00463522d48942210c000000/MT-SUMMIT13Language-independent-Model-for-Machine-Translation-Evaluation-with-Reinforced-Factors.pdf
    >>> reference = 'It is a guide to action that ensures that the military will forever heed Party commands'
    >>> hypothesis = 'It is a guide to action which ensures that the military always obeys the commands of the party'
    >>> round(single_hlepor_score(reference, hypothesis), 4)
    0.7842
    :param reference: reference sentence
    :param hypothesis: hypothesis sentence
    :param alpha: the tunable weight for recall
    :param beta: the tunable weight for precision
    :param n: words count before and after matched word in npd calculation
    :param weight_elp: tunable weight of enhanced length penalty
    :param weight_pos: tunable weight of n-gram position difference penalty
    :param weight_pr: tunable weight of harmonic mean of precision and recall
    :param weight_pr: tunable weight of harmonic mean of precision and recall
    :param preprocess: preprocessing method
    :param separate_punctuation: with the separation of punctuation from words(True value) or not(False)
    :param language: language of the reference and hypothesis
    :return: the sentence-level hLepor score
    """
    return hlepor_score([reference], [hypothesis], alpha, beta, n, weight_elp, weight_pos,
                        weight_pr, preprocess, separate_punctuation, language)
