from BERT import BERTModel
import numpy as np

class AI():
    def __init__(self):
        self.BERTModel = BERTModel('./models/MLTC_model_state.bin')
    
    def ESG_scores_prediction(self, chain):
        if len(chain) == 1:
            return [[0, 0, 0]]
        BERT_input = self.extract_data(chain)
        BERT_predictions, BERT_predictions_prob = self.BERTModel.get_predictions(BERT_input)
        
        BERT_predictions_prob = np.array(BERT_predictions_prob)
        N = BERT_predictions_prob.shape[0]

        # Remove the probabilities that are < 0.5 (classification threshold)
        BERT_predictions_prob[BERT_predictions_prob < 0.5] = 0

        # Normalize the result by ([probabilities which are > 0.5] - 0.5) / 0.5, ignoring 0s
        nonzero_indices = BERT_predictions_prob != 0
        normalized_prob = np.zeros_like(BERT_predictions_prob)
        normalized_prob[nonzero_indices] = (BERT_predictions_prob[nonzero_indices] - 0.5) / 0.5

        # Add weight = 0.1 (each subtopic is 1/10 of E, S, or G)
        normalized_prob = normalized_prob * 0.1

        # For each course, calculate its ESG scores
        normalized_prob_each = normalized_prob.reshape((N, 3, 10))
        each_ESG_scores = np.sum(normalized_prob_each, axis=2).tolist()
        
        # To calculate the total ESG scores,
        # Sum the result element-wise by column (subtopic) 
        sum_prob_subtopics = np.sum(normalized_prob, axis=0)
        
        # Reshape the result to (3, 10) and sum it element-wise by row to get the total score of each E, S, and G, cap maximum at 1
        sum_prob_subtopics = sum_prob_subtopics.reshape((3, 10))
        total_ESG_scores = np.sum(sum_prob_subtopics, axis=1)
        total_ESG_scores[total_ESG_scores > 1] = 1
        total_ESG_scores = total_ESG_scores.tolist()
        
        return [total_ESG_scores] + each_ESG_scores
    
    def extract_data(self, chain):
        chain = chain[1:]
        all_combined = []
        for block in chain:
            combined = block.data['course_title'] + '. ' + block.data['course_description']
            all_combined.append(combined)

        return all_combined
    


