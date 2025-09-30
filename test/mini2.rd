IN sets (Reaching Definitions)
  entry: {}
  L1: {entry:a@0, entry:b@1}
  L2: {entry:a@0, entry:b@1}
  L3: {L1:c@1, entry:a@0, entry:b@1}

OUT sets (Reaching Definitions)
  entry: {entry:a@0, entry:b@1}
  L1: {L1:c@1, entry:a@0, entry:b@1}
  L2: {L1:c@1, entry:a@0, entry:b@1}
  L3: {L1:c@1, L3:d@1, entry:a@0, entry:b@1}

