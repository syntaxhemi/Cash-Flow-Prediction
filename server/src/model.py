import torch
import torch.nn as nn

from src.env import vars

class TemporalStaticFusion(nn.Module):
    def __init__(
        self, 
        seq_input_size, 
        static_input_size, 
        lstm_hidden=128, 
        dense_hidden=64
    ) -> None:
        super(TemporalStaticFusion, self).__init__()

        self.lstm = nn.LSTM(
            input_size=seq_input_size, 
            hidden_size=lstm_hidden, 
            batch_first=True,
            dropout=0.3
        )
        self.seq_block = nn.Sequential(
            nn.Linear(lstm_hidden, dense_hidden),
            nn.BatchNorm1d(dense_hidden),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        self.static_block = nn.Sequential(
            nn.Linear(static_input_size, dense_hidden),
            nn.BatchNorm1d(dense_hidden),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        self.fusion_block = nn.Sequential(
            nn.Linear(dense_hidden * 2, dense_hidden),
            nn.BatchNorm1d(dense_hidden),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        self.output_layer = nn.Linear(dense_hidden, 1)


    def forward(self, input_seq, input_static):
        seq_output, _ = self.lstm(input_seq)
        seq_pooled = torch.mean(seq_output, dim=1)  # temporal pooling

        seq_feat = self.seq_block(seq_pooled)
        static_feat = self.static_block(input_static)

        fused = torch.cat((seq_feat, static_feat), dim=1)
        fused = self.fusion_block(fused)
        out = self.output_layer(fused)
        return out

model = TemporalStaticFusion(
    vars.SEQ_INPUT_SIZE, 
    vars.STATIC_INPUT_SIZE, 
    vars.LSTM_HIDDEN, 
    vars.DENSE_HIDDEN
)
model.load_state_dict(torch.load(f'{vars.ASSETS_DIR}/{vars.MODEL_PARAMS_PATH}'))
model.eval()
