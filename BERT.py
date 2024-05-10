import torch
from transformers import BertTokenizer, BertModel


class BERTClass(torch.nn.Module):
    def __init__(self):
        super(BERTClass, self).__init__()
        self.bert_model = BertModel.from_pretrained('bert-base-uncased', return_dict=True)
        self.dropout = torch.nn.Dropout(0.3)
        self.linear = torch.nn.Linear(768, 30)

    def forward(self, input_ids, attn_mask, token_type_ids):
        output = self.bert_model(
            input_ids, 
            attention_mask=attn_mask, 
            token_type_ids=token_type_ids
        )
        output_dropout = self.dropout(output.pooler_output)
        output = self.linear(output_dropout)
        return output
    
class BERTModel():
    def __init__(self, trained_model_path):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BERTClass()
        self.model.load_state_dict(torch.load(trained_model_path))
        self.model = self.model.to(self.device)
        self.model = self.model.eval()

    def get_predictions(self, input):
        all_predictions = []
        all_predictions_prob = []

        for raw_text in input:
            encoded_text = self.tokenizer.encode_plus(
                raw_text,
                None,
                add_special_tokens=True,
                max_length=256,
                padding='max_length',
                return_token_type_ids=True,
                truncation=True,
                return_attention_mask=True,
                return_tensors='pt'
            )

            input_ids = encoded_text['input_ids'].to(self.device)
            attention_mask = encoded_text['attention_mask'].to(self.device)
            token_type_ids = encoded_text['token_type_ids'].to(self.device)

            output = self.model(input_ids, attention_mask, token_type_ids)

            # add sigmoid, for the training sigmoid is in BCEWithLogitsLoss
            predictions_prob = torch.sigmoid(output).detach().cpu()
            # thresholding at 0.5
            predictions = predictions_prob.flatten().round()

            all_predictions.append(predictions.tolist())
            all_predictions_prob.append(predictions_prob.tolist())

        return all_predictions, all_predictions_prob