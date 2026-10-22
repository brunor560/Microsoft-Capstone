"""Test package. Drafting with Azure is on by default (drafting.json); tests force it off so
no test can reach Azure or read pipeline/autogen/.env. Tests that need it pass --draft or
patch APPROACH_A_DRAFT themselves, always with a fake endpoint."""
import os

os.environ['APPROACH_A_DRAFT'] = 'off'

