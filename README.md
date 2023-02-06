# Propose changes to ERC721A

This contract is for testing and proof of concept purpose only, DYOR

----

When user batch mint with {_mintERC2309} function, there is large in consistency in gas used by {transferFrom} {safeTransferFrom} {_burn} functions, and the most of these gas is use in {_packedOwnershipOf} function [see ERC721A ](https://github.com/chiru-labs/ERC721A/blob/eb4fad60f826bed543cdb0fee54fe1a256d8c0f5/contracts/ERC721A.sol#L346) . when the `_packedOwnerships[tokenId]` of a Token is not initialized the ERC721A initiate a sequential search for an initialized token toward tokenId `0` in descending order.
```solidity

      // If the address is zero, packed will be zero.
      for (;;) {
          unchecked {
              packed = _packedOwnerships[--tokenId];
          }
          if (packed == 0) continue;
          return packed;
      }
```
since the `_MAX_MINT_ERC2309_QUANTITY_LIMIT = 5000;` can be up to 5000 tokens there could be a big difference of gas when you transfer token depending on the distance of it to last initialized tokenId [chiru-labs: ERC721A Tips here](https://chiru-labs.github.io/ERC721A/#/tips?id=transfers) 
for example you can see these example
tokenId `0` transfer : distance to last initialize tokenId = 0 : gas used = 83,607: [goerli-etherscan](https://goerli.etherscan.io/tx/0x988eda3d87e9a370721282a981451c5b1b887dacee1c145bb5faaeeeb01c8a61)
tokenId `4999` transfer : distance to last initialize tokenId = 4998 : gas used = 11,099,130: [goerli-etherscan](https://goerli.etherscan.io/tx/0x4d87d29888803bbfef5125ab519f1ab3eef547d8457111cff27c2ccd8b14d4a1)
tokenId `7499` transfer : distance to last initialize tokenId = 2500: gas used =  5,601,5350: [goerli-etherscan](https://goerli.etherscan.io/tx/0x9a1b1d7229d6f97e6e8d3d7a10539fa76a278d2546034d138d70ab4dc4987d4f)

---
## proof of concept
I used a striped down version of  openZeppelin [Checkpoints.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Checkpoints.sol#L364) to track the starting tokenId of each batch for batch minter, like in [ERC721Consecutive](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721Consecutive.sol) .
```solidity 

//proposed changes
    using Checkpoints for Checkpoints.Trace160;
    Checkpoints.Trace160 private _sequentialOwnership;

 function _mintERC2309(address to, uint256 quantity) internal virtual {
        uint256 startTokenId = _currentIndex;
        if (to == address(0)) _revert(MintToZeroAddress.selector);
        if (quantity == 0) _revert(MintZeroQuantity.selector);
        if (quantity > _MAX_MINT_ERC2309_QUANTITY_LIMIT)
            _revert(MintERC2309QuantityExceedsLimit.selector);

        _beforeTokenTransfers(address(0), to, startTokenId, quantity);

        // Overflows are unrealistic due to the above check for `quantity` to be below the limit.
        unchecked {
            // Updates:
            // - `balance += quantity`.
            // - `numberMinted += quantity`.
            //
            // We can directly add to the `balance` and `numberMinted`.
            _packedAddressData[to] +=
                quantity *
                ((1 << _BITPOS_NUMBER_MINTED) | 1);

            
            // --------------Omited - since we have the data in _sequentialOwnership
            // _packedOwnerships[startTokenId] = _packOwnershipData(
            //     to,
            //     _nextInitializedFlag(quantity) |
            //         _nextExtraData(address(0), to, 0)
            // );
            //
            uint96 last = uint96(startTokenId + quantity - 1);
            _sequentialOwnership.push(last, uint160(to));
            //
            emit ConsecutiveTransfer(
                startTokenId,
                startTokenId + quantity - 1,
                address(0),
                to
            );

            _currentIndex = startTokenId + quantity;
        }
        _afterTokenTransfers(address(0), to, startTokenId, quantity);
    }

//--------- getbatch minted range
      function _totalConsecutiveSupply() private view returns (uint96) {
        (bool exists, uint96 latestId, ) = _sequentialOwnership
            .latestCheckpoint();
        return exists ? latestId + 1 : 0;
    }
//---------
 /**
     * Returns the packed ownership data of `tokenId`.
     */
    function _packedOwnershipOf(uint256 tokenId)
        private
        view
        returns (uint256 packed)
    {
        if (_startTokenId() <= tokenId) {
            packed = _packedOwnerships[tokenId];
            // If not burned.
            if (packed & _BITMASK_BURNED == 0) {
                // If the data at the starting slot does not exist, start the scan.
                if (packed == 0) {
                    if (tokenId >= _currentIndex)
                        _revert(OwnerQueryForNonexistentToken.selector);
                    // Invariant:
                    // There will always be an initialized ownership slot
                    // (i.e. `ownership.addr != address(0) && ownership.burned == false`)
                    // before an unintialized ownership slot
                    // (i.e. `ownership.addr == address(0) && ownership.burned == false`)
                    // Hence, `tokenId` will not underflow.
                    //
                    //binary search for ERC2309 minted tokens more efficient than sequential search
                   //only if it is in batch minted range
                    if (tokenId < _totalConsecutiveSupply()) {
                        return
                            uint256(
                                _sequentialOwnership.lowerLookup(
                                    uint96(tokenId)
                                ) | _BITMASK_NEXT_INITIALIZED // all batch minted token are initialized
                            );
                    }
                    // consider all of the batch minted token initialized since if they can be find with binary search above
                    //  this benefits user by preventing the token to initialize the next tokneId 
                    // at the end of {transferFrom} and {_burn} functions
                    //------
                    // if token was minted with {_mint} function and is not initialized sequential search bellow will find it.
                    // We can directly compare the packed value.
                    // If the address is zero, packed will be zero.
                    for (;;) {
                        unchecked {
                            packed = _packedOwnerships[--tokenId];
                        }
                        if (packed == 0) continue;
                        return packed;
                    }
                }
                // Otherwise, the data exists and is not burned. We can skip the scan.
                // This is possible because we have already achieved the target condition.
                // This saves 2143 gas on transfers of initialized tokens.
                return packed;
            }
        }
        _revert(OwnerQueryForNonexistentToken.selector);
    }

```
I deployed this on testnet [modified test Contract](https://goerli.etherscan.io/token/0x85ec9178fb0e1689a955a0bf23892528e3925221#code)
tokenId `0` transfer : distance to last initialize tokenId = 0 : gas used = 88,591: [goerli-etherscan](https://goerli.etherscan.io/tx/0x0c7d7054c06a513754191c680349c64df46ffcbbaa46efc733f5616f18e53ab6)
tokenId `4999` transfer : distance to last initialize tokenId = 4998 : gas used = 71,515 : [goerli-etherscan](https://goerli.etherscan.io/tx/0xcc72edc1664fff86c1a41a9233c7a884ff295099414e332e915c668bcda361ed)
tokenId `7499` transfer : distance to last initialize tokenId = 2500: gas used =  71,592 : [goerli-etherscan](https://goerli.etherscan.io/tx/0x47935037b401bab22c2335312ea247d5daf698b3513ebed00ef6bb47e7132a0f)
full implementation is available GitHub [ERC721AModified.sol](https://github.com/shypink/ERC721AModified/blob/master/contracts/ERC721AToken.sol) 

-----
SCINFTIST.ETH